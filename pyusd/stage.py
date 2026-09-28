from __future__ import annotations

import os
from typing import Any, Iterable, List, Optional, Type, TypeVar, Union

from .attribute import Attribute
from .composition import (
    CompositionEngine,
    LayerCache,
    normalize_prim_path,
    normalize_property_name,
    path_items,
    prim_at,
    property_value,
)
from .layer import Layer
from .prim import Prim
from .property import Property
from .relationship import Relationship
from .sdf import Specifier
from .utils import infer_type

PrimType = TypeVar("PrimType", bound=Prim)


class StageImpl:
    def __init__(self, root_layer: Layer, edit_layer: Optional[Layer] = None) -> None:
        self.root_layer = root_layer
        self.edit_layer = edit_layer or root_layer
        self.layer_cache = LayerCache()
        self._engine = CompositionEngine(root_layer, self.layer_cache)


class Stage:
    _impl_fields = {"root_layer", "edit_layer", "layer_cache", "_engine"}

    def __init__(
        self,
        root_layer: Union[str, Layer] = "",
        edit_layer: Optional[Layer] = None,
    ) -> None:
        if isinstance(root_layer, Layer):
            resolved_root = root_layer
        else:
            file_name = str(root_layer)
            resolved_root = Layer._lookup(file_name)
            if resolved_root is None:
                if file_name and os.path.exists(Layer._registry_key(file_name)):
                    resolved_root = Layer.load(file_name)
                else:
                    resolved_root = Layer(file_name)

        object.__setattr__(self, "_impl", StageImpl(resolved_root, edit_layer))

    def __getattr__(self, name: str) -> Any:
        if name in self._impl_fields:
            return getattr(self._impl, name)

        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_impl":
            object.__setattr__(self, name, value)
        elif name in self._impl_fields and "_impl" in self.__dict__:
            setattr(self._impl, name, value)
        else:
            object.__setattr__(self, name, value)

    @staticmethod
    def open(file_name: str) -> Stage:
        return Stage(file_name)

    @staticmethod
    def from_layer(layer: Layer, edit_layer: Optional[Layer] = None) -> Stage:
        return Stage(layer, edit_layer)

    @property
    def layer_stack(self) -> List[Layer]:
        return self._engine.layer_stack(self.root_layer)

    @property
    def layers(self) -> List[Layer]:
        return self.layer_stack

    def get_layer(self, file_name: str) -> Optional[Layer]:
        if Layer._registry_key(file_name) == Layer._registry_key(self.root_layer.file_name):
            return self.root_layer

        for layer in self.layer_stack:
            if Layer._registry_key(layer.file_name) == Layer._registry_key(
                file_name,
                self.root_layer.file_name,
            ):
                return layer

        layer = Layer._lookup(file_name, self.root_layer.file_name)
        if layer is not None:
            return layer

        resolved_name = Layer._registry_key(file_name, self.root_layer.file_name)
        if resolved_name and os.path.exists(resolved_name):
            return Layer.load(resolved_name)

        return None

    def get_source_layer(self, path: str) -> Optional[Layer]:
        spec = self._engine.prim_index(path).strongest_spec
        return spec.layer if spec is not None else None

    @property
    def metadata(self) -> StageMetadata:
        return StageMetadata(self, None)

    @property
    def default_prim(self) -> Optional[StagePrim]:
        default_prim = self._engine.resolve_metadata(None, "defaultPrim")
        if default_prim is None:
            return None

        if isinstance(default_prim, Prim):
            return self[default_prim.path]

        path = str(default_prim)
        if not path.startswith("/"):
            path = "/" + path

        if not self.has_prim(path):
            return None

        return self[path]

    def invalidate(self) -> None:
        self._engine.clear()

    def has_prim(self, path: str) -> bool:
        return self._engine.has_prim(path)

    def child_names(self, path: str = "/") -> List[str]:
        return self._engine.child_names(path)

    def children(self, path: str = "/") -> List[StagePrim]:
        return [self[join_relative_path(path, name)] for name in self.child_names(path)]

    def traverse(self, path: str = "/") -> Iterable[StagePrim]:
        path = normalize_prim_path(path)
        if path != "/":
            yield self[path]

        for child_name in self.child_names(path):
            child_path = join_relative_path(path, child_name)
            yield from self.traverse(child_path)

    def load(self, path: str = "") -> None:
        if not path:
            self._engine.load_payloads = True
            self._engine.unloaded_payloads.clear()
        else:
            self._engine.unloaded_payloads.discard(normalize_prim_path(path))
        self.invalidate()

    def unload(self, path: str = "") -> None:
        if not path:
            self._engine.load_payloads = False
        else:
            self._engine.unloaded_payloads.add(normalize_prim_path(path))
        self.invalidate()

    def __getitem__(self, path: str) -> StagePrim:
        path = normalize_prim_path(path)
        if path != "/" and not self.has_prim(path):
            raise KeyError(path)

        return StagePrim(self, path)

    def __setitem__(self, path: str, prim: Prim) -> None:
        self.edit_layer[normalize_prim_path(path)] = prim
        self.invalidate()

    def __delitem__(self, path: str) -> None:
        del self.edit_layer[normalize_prim_path(path)]
        self.invalidate()

    def def_(self, prim_type: Type[PrimType], path: str) -> StagePrim:
        prim = prim_type(specifier=Specifier.Def)
        self.edit_layer[normalize_prim_path(path)] = prim
        self.invalidate()
        return self[path]

    def class_(self, path: str) -> StagePrim:
        prim = Prim(specifier=Specifier.Class)
        self.edit_layer[normalize_prim_path(path)] = prim
        self.invalidate()
        return self[path]

    def over_(self, path: str) -> StagePrim:
        prim = Prim(specifier=Specifier.Over)
        self.edit_layer[normalize_prim_path(path)] = prim
        self.invalidate()
        return self[path]

    def _ensure_edit_prim(self, path: str) -> Prim:
        path = normalize_prim_path(path)
        if path == "/":
            raise ValueError("cannot author the pseudo-root prim")

        prim = prim_at(self.edit_layer, path)
        if prim is not None:
            return prim

        self.edit_layer[path] = Prim(specifier=Specifier.Over)
        prim = prim_at(self.edit_layer, path)
        if prim is None:
            raise RuntimeError(f"failed to create edit prim at {path}")

        return prim

    def _set_property(self, prim_path: str, prop_name: str, value: Any) -> Property:
        prim_path = normalize_prim_path(prim_path)
        prop_name = normalize_property_name(prop_name)
        template = self._engine.resolve_property(prim_path, prop_name)
        edit_prim = self._ensure_edit_prim(prim_path)

        if isinstance(value, Property):
            prop = value.clone()
            prop._name = prop_name.split(":")[-1]
            self._install_property(edit_prim, prop_name, prop)
            self.invalidate()
            return prop

        if isinstance(template, Relationship) or is_relationship_value(value):
            rel = self._ensure_edit_relationship(edit_prim, prop_name, template)
            rel._targets = coerce_relationship_targets(value)
            rel._value_state = Property.ValueState.Authored
            self.invalidate()
            return rel

        attr = self._ensure_edit_attribute(edit_prim, prop_name, template, value)
        attr.set(value)
        self.invalidate()
        return attr

    def _create_attribute(
        self,
        prim_path: str,
        prop_name: str,
        value_type: type,
        value: Any = None,
        doc: str = "",
        metadata: Optional[dict] = None,
        is_leaf: bool = True,
        uniform: bool = False,
        custom: bool = True,
        fix_type: bool = True,
    ) -> StageProperty:
        edit_prim = self._ensure_edit_prim(prim_path)
        prop_name = normalize_property_name(prop_name)
        attr = Attribute(
            value_type,
            name=prop_name.split(":")[-1],
            value=None,
            doc=doc,
            metadata=metadata,
            is_leaf=is_leaf,
            uniform=uniform,
            custom=custom,
            fix_type=fix_type,
        )
        attr._value_state = Property.ValueState.NotAuthored
        self._install_property(edit_prim, prop_name, attr)
        if value is not None:
            attr.set(value)
        self.invalidate()
        return StageProperty(self, prim_path, prop_name)

    def _create_relationship(
        self,
        prim_path: str,
        prop_name: str,
        targets: Any = None,
        doc: str = "",
        metadata: Optional[dict] = None,
        custom: bool = True,
        is_leaf: bool = True,
    ) -> StageProperty:
        edit_prim = self._ensure_edit_prim(prim_path)
        prop_name = normalize_property_name(prop_name)
        rel = Relationship(
            name=prop_name.split(":")[-1],
            doc=doc,
            metadata=metadata,
            custom=custom,
            is_leaf=is_leaf,
        )
        rel._value_state = Property.ValueState.NotAuthored
        if targets is not None:
            rel._targets = coerce_relationship_targets(targets)
            rel._value_state = Property.ValueState.Authored
        self._install_property(edit_prim, prop_name, rel)
        self.invalidate()
        return StageProperty(self, prim_path, prop_name)

    def _set_metadata(self, prim_path: Optional[str], key: str, value: Any, prop_name: str = "") -> None:
        if prim_path is None:
            setattr(self.edit_layer.metadata, key, value)
            self.invalidate()
            return

        edit_prim = self._ensure_edit_prim(prim_path)
        if prop_name:
            template = self._engine.resolve_property(prim_path, prop_name)
            prop = self._ensure_edit_property(edit_prim, prop_name, template)
            setattr(prop.metadata, key, value)
        else:
            setattr(edit_prim.metadata, key, value)

        self.invalidate()

    def _install_property(self, prim: Prim, prop_name: str, prop: Property) -> Property:
        names = normalize_property_name(prop_name).split(":")
        current: Union[Prim, Property] = prim
        for name in names[:-1]:
            props = current._props
            if name not in props:
                namespace_prop = Property(name, custom=True, is_leaf=False)
                current.create_prop(namespace_prop)
            current = props[name]

        prop._name = names[-1]
        current.create_prop(prop)
        return prop

    def _ensure_edit_property(
        self,
        prim: Prim,
        prop_name: str,
        template: Optional[Property],
    ) -> Property:
        prop_name = normalize_property_name(prop_name)
        existing = local_prop_at(prim, prop_name)
        if existing is not None:
            return existing

        if template is not None:
            prop = clone_for_edit(template)
        else:
            prop = Property(prop_name.split(":")[-1], custom=True, is_leaf=False)

        return self._install_property(prim, prop_name, prop)

    def _ensure_edit_attribute(
        self,
        prim: Prim,
        prop_name: str,
        template: Optional[Property],
        value: Any,
    ) -> Attribute:
        existing = local_prop_at(prim, prop_name)
        if isinstance(existing, Attribute):
            return existing

        if isinstance(template, Attribute):
            attr = clone_for_edit(template)
            if not isinstance(attr, Attribute):
                raise TypeError("template clone did not produce an Attribute")
        else:
            value_type = str if value is None else infer_type(value)
            attr = Attribute(value_type, prop_name.split(":")[-1], custom=True, fix_type=False)
            attr._value_state = Property.ValueState.NotAuthored

        self._install_property(prim, prop_name, attr)
        return attr

    def _ensure_edit_relationship(
        self,
        prim: Prim,
        prop_name: str,
        template: Optional[Property],
    ) -> Relationship:
        existing = local_prop_at(prim, prop_name)
        if isinstance(existing, Relationship):
            return existing

        if isinstance(template, Relationship):
            rel = clone_for_edit(template)
            if not isinstance(rel, Relationship):
                raise TypeError("template clone did not produce a Relationship")
        else:
            rel = Relationship(prop_name.split(":")[-1], custom=True)
            rel._value_state = Property.ValueState.NotAuthored

        self._install_property(prim, prop_name, rel)
        return rel


class StagePrim:
    def __init__(self, stage: Stage, path: str) -> None:
        object.__setattr__(self, "_stage", stage)
        object.__setattr__(self, "_path", normalize_prim_path(path))

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        items = path_items(self._path)
        return items[-1] if items else ""

    @property
    def metadata(self) -> StageMetadata:
        return StageMetadata(self._stage, self._path)

    @property
    def resolved_prim(self) -> Optional[Prim]:
        strongest = self._stage._engine.prim_index(self._path).strongest_spec
        return strongest.prim if strongest is not None else None

    @property
    def specifier(self) -> Optional[Specifier]:
        prim = self.resolved_prim
        return prim.specifier if prim is not None else None

    @property
    def type_name(self) -> Optional[str]:
        return self._stage._engine.resolve_metadata(self._path, "typeName")

    @property
    def child_names(self) -> List[str]:
        return self._stage.child_names(self._path)

    @property
    def children(self) -> List[StagePrim]:
        return [self.child(name) for name in self.child_names]

    @property
    def prop_names(self) -> List[str]:
        names = self._stage._engine.property_names(self._path)
        return [name for name in names if ":" not in name]

    @property
    def props(self) -> List[StageProperty]:
        return [StageProperty(self._stage, self._path, name) for name in self.prop_names]

    def has_prop(self, name: str) -> bool:
        return self._stage._engine.resolve_property(self._path, name) is not None

    def prop(self, name: str) -> StageProperty:
        if not self.has_prop(name):
            raise KeyError(name)

        return StageProperty(self._stage, self._path, name)

    def child(self, name: str) -> StagePrim:
        return self[join_relative_path("", name)]

    def def_(self, prim_type: Type[PrimType], path: str) -> StagePrim:
        return self._stage.def_(prim_type, join_relative_path(self._path, path))

    def class_(self, path: str) -> StagePrim:
        return self._stage.class_(join_relative_path(self._path, path))

    def over_(self, path: str) -> StagePrim:
        return self._stage.over_(join_relative_path(self._path, path))

    def __getitem__(self, path: str) -> StagePrim:
        return self._stage[join_relative_path(self._path, path)]

    def __setitem__(self, path: str, prim: Prim) -> None:
        self._stage[join_relative_path(self._path, path)] = prim

    def __delitem__(self, path: str) -> None:
        del self._stage[join_relative_path(self._path, path)]

    def __getattr__(self, name: str) -> StageProperty:
        return StageProperty(self._stage, self._path, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_") or hasattr(self.__class__, name):
            object.__setattr__(self, name, value)
            return

        self._stage._set_property(self._path, name, value)

    def __str__(self) -> str:
        return f"StagePrim(<{self._path}>)"

    def __repr__(self) -> str:
        return str(self)


class StageProperty:
    def __init__(self, stage: Stage, prim_path: str, prop_name: str) -> None:
        object.__setattr__(self, "_stage", stage)
        object.__setattr__(self, "_prim_path", normalize_prim_path(prim_path))
        object.__setattr__(self, "_prop_name", normalize_property_name(prop_name))

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def prim_path(self) -> str:
        return self._prim_path

    @property
    def name(self) -> str:
        return self._prop_name.split(":")[-1]

    @property
    def full_name(self) -> str:
        return self._prop_name

    @property
    def path(self) -> str:
        return f"{self._prim_path}.{self._prop_name}"

    @property
    def metadata(self) -> StageMetadata:
        return StageMetadata(self._stage, self._prim_path, self._prop_name)

    @property
    def resolved_property(self) -> Optional[Property]:
        return self._stage._engine.resolve_property(self._prim_path, self._prop_name)

    @property
    def exists(self) -> bool:
        return self.resolved_property is not None

    @property
    def value(self) -> Any:
        return self.get()

    @value.setter
    def value(self, value: Any) -> None:
        self.set(value)

    @property
    def targets(self) -> List[Any]:
        prop = self.resolved_property
        if isinstance(prop, Relationship):
            return prop.targets

        return []

    @property
    def timeSamples(self) -> dict:
        prop = self.resolved_property
        if isinstance(prop, Attribute):
            return prop.timeSamples

        return {}

    @property
    def value_state(self) -> Optional[Property.ValueState]:
        prop = self.resolved_property
        return prop.value_state if prop is not None else None

    @property
    def type(self) -> Optional[type]:
        prop = self.resolved_property
        return prop.type if isinstance(prop, Attribute) else None

    @property
    def type_name(self) -> str:
        prop = self.resolved_property
        return prop.type_name if isinstance(prop, Attribute) else ""

    @property
    def custom(self) -> bool:
        prop = self.resolved_property
        return prop.custom if prop is not None else True

    @property
    def is_leaf(self) -> bool:
        prop = self.resolved_property
        return prop.is_leaf if prop is not None else True

    def get(self) -> Any:
        return property_value(self.resolved_property)

    def set(self, value: Any) -> None:
        self._stage._set_property(self._prim_path, self._prop_name, value)

    def clear(self) -> None:
        prop = self._stage._ensure_edit_property(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        if isinstance(prop, Attribute):
            prop.clear()
        elif isinstance(prop, Relationship):
            prop._targets = []
            prop._value_state = Property.ValueState.Cleared
        else:
            prop._value_state = Property.ValueState.Cleared
        self._stage.invalidate()

    def create(
        self,
        value_type: type,
        value: Any = None,
        uniform: bool = False,
        custom: bool = True,
        fix_type: bool = True,
    ) -> StageProperty:
        return self._stage._create_attribute(
            self._prim_path,
            self._prop_name,
            value_type,
            value=value,
            uniform=uniform,
            custom=custom,
            fix_type=fix_type,
        )

    def rel(self, prim: Any) -> StageProperty:
        return self._stage._create_relationship(self._prim_path, self._prop_name, prim)

    def add_target(self, prim: Any) -> None:
        rel = self._stage._ensure_edit_relationship(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        rel._targets.extend(coerce_relationship_targets(prim))
        rel._value_state = Property.ValueState.Authored
        self._stage.invalidate()

    def remove_target(self, prim: Any) -> None:
        targets = coerce_relationship_targets(prim)
        rel = self._stage._ensure_edit_relationship(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        for target in targets:
            if target in rel._targets:
                rel._targets.remove(target)
        rel._value_state = Property.ValueState.Authored
        self._stage.invalidate()

    def __getattr__(self, name: str) -> Any:
        child_name = self._prop_name + ":" + name
        if self._stage._engine.resolve_property(self._prim_path, child_name) is not None:
            return StageProperty(self._stage, self._prim_path, child_name)

        value = self.get()
        if value is not None and hasattr(value, name):
            return getattr(value, name)

        return StageProperty(self._stage, self._prim_path, child_name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_") or hasattr(self.__class__, name):
            object.__setattr__(self, name, value)
            return

        self._stage._set_property(self._prim_path, self._prop_name + ":" + name, value)

    def __str__(self) -> str:
        return str(self.get())

    def __repr__(self) -> str:
        return repr(self.get())

    def __bool__(self) -> bool:
        return bool(self.get())

    def __len__(self) -> int:
        return len(self.get())

    def __iter__(self):
        return iter(self.get())

    def __getitem__(self, key: Any) -> Any:
        return self.get()[key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StageProperty):
            other = other.get()
        return self.get() == other

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class StageMetadata:
    def __init__(self, stage: Stage, prim_path: Optional[str], prop_name: str = "") -> None:
        object.__setattr__(self, "_stage", stage)
        object.__setattr__(self, "_prim_path", normalize_prim_path(prim_path) if prim_path else None)
        object.__setattr__(self, "_prop_name", normalize_property_name(prop_name) if prop_name else "")

    def get(self, key: str, default: Any = None) -> Any:
        value = self._stage._engine.resolve_metadata(self._prim_path, key, self._prop_name)
        return default if value is None else value

    def set(self, key: str, value: Any) -> None:
        self._stage._set_metadata(self._prim_path, key, value, self._prop_name)

    def __getattr__(self, name: str) -> Any:
        value = self._stage._engine.resolve_metadata(self._prim_path, name, self._prop_name)
        if value is None:
            raise AttributeError(name)

        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_") or hasattr(self.__class__, name):
            object.__setattr__(self, name, value)
            return

        self.set(name, value)


def clone_for_edit(prop: Property) -> Property:
    result = prop.clone()
    result._parent = None
    if isinstance(result, Attribute):
        result._time_samples = {}
        result._value_state = Property.ValueState.NotAuthored
    elif isinstance(result, Relationship):
        result._targets = []
        result._value_state = Property.ValueState.NotAuthored
    else:
        result._value_state = Property.ValueState.NotAuthored

    return result


def local_prop_at(prim: Prim, prop_name: str) -> Optional[Property]:
    names = normalize_property_name(prop_name).split(":")
    current: Any = prim
    for name in names:
        if name not in current._props:
            return None
        current = current._props[name]

    return current


def is_relationship_value(value: Any) -> bool:
    if isinstance(value, (Prim, StagePrim, Relationship)):
        return True

    if isinstance(value, list) and value:
        return all(isinstance(item, (Prim, StagePrim)) or is_path_target(item) for item in value)

    return is_path_target(value)


def is_path_target(value: Any) -> bool:
    return isinstance(value, str) and (
        value.startswith("<") or value.startswith("/") or value.startswith("@")
    )


def coerce_relationship_targets(value: Any) -> List[Any]:
    if isinstance(value, Relationship):
        return list(value.targets)

    if not isinstance(value, list):
        value = [value]

    result: List[Any] = []
    for item in value:
        if isinstance(item, StagePrim):
            result.append(f"<{item.path}>")
        elif isinstance(item, Prim):
            result.append(item)
        elif isinstance(item, str):
            if item.startswith("<") or item.startswith("@"):
                result.append(item)
            else:
                result.append(f"<{normalize_prim_path(item)}>")
        else:
            result.append(item)

    return result


def join_relative_path(base_path: str, path: str) -> str:
    base_path = normalize_prim_path(base_path) if base_path else ""
    path = str(path)
    if path.startswith("/"):
        return normalize_prim_path(path)

    if not base_path or base_path == "/":
        return normalize_prim_path("/" + path)

    return normalize_prim_path(base_path + "/" + path)
