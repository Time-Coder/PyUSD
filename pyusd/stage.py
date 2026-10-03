"""Stage: a composed view over a root layer, and the edit target that authors it.

The prim view lives in :mod:`pyusd.prim`; property, metadata, and variant views in
their own modules. This module holds the stage itself plus the plumbing that
writes opinions into the edit layer.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union, cast

from .attribute import Attribute
from .attribute_spec import AttributeSpec
from .composition import CompositionEngine, LayerCache
from .layer import Layer
from .prim import Prim, PrimType
from .prim_spec import PrimSpec
from .property import Property
from .property_spec import PropertySpec
from .relationship import Relationship
from .relationship_spec import RelationshipSpec
from .sdf import Specifier
from .stage_metadata import StageMetadata
from .utils import (
    in_annotations,
    infer_type,
    join_relative_path,
    normalize_prim_path,
    normalize_property_name,
    prim_at,
)


class StageImpl:
    root_layer: Layer
    edit_layer: Layer
    layer_cache: LayerCache
    _engine: CompositionEngine
    prim_views: Dict[Tuple[str, type], Prim]

    def __init__(self, root_layer: Layer, edit_layer: Optional[Layer] = None) -> None:
        self.root_layer = root_layer
        self.edit_layer = edit_layer or root_layer
        self.layer_cache = LayerCache()
        self._engine = CompositionEngine(root_layer, self.layer_cache)
        # One Prim view per (path, class), so asking a stage for the same path twice
        # hands back the same object. Keying on the class rather than the path alone
        # is what keeps this correct without an invalidation hook: the class comes from
        # the composed typeName, so a stronger layer that retypes a prim lands on a
        # different key and the stale view is never handed out again. It stays in the
        # dict, unreferenced by anything but itself.
        self.prim_views: Dict[Tuple[str, type], Prim] = {}


class Stage:
    _impl: StageImpl
    root_layer: Layer
    edit_layer: Layer
    layer_cache: LayerCache
    _engine: CompositionEngine
    prim_views: Dict[Tuple[str, type], Prim]

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
        if name != "_impl" and in_annotations(name, self.__class__):
            return getattr(self._impl, name)

        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_impl":
            object.__setattr__(self, name, value)
        elif in_annotations(name, self.__class__) and "_impl" in self.__dict__:
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
    def default_prim(self) -> Optional[Prim]:
        default_prim = self._engine.resolve_metadata(None, "defaultPrim")
        if default_prim is None:
            return None

        if isinstance(default_prim, PrimSpec):
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

    def stage_has_prim(self, path: str) -> Optional[Prim]:
        """Return the prim view at ``path``, or None when it is not populated."""
        path = normalize_prim_path(path)
        if path == "/":
            return self[path]

        if not self.has_prim(path):
            return None

        return self[path]

    def child_names(self, path: str = "/") -> List[str]:
        return self._engine.child_names(path)

    def children(self, path: str = "/") -> List[Prim]:
        return [self[join_relative_path(path, name)] for name in self.child_names(path)]

    def traverse(self, path: str = "/") -> Iterable[Prim]:
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

    def __getitem__(self, path: str) -> Prim:
        path = normalize_prim_path(path)
        # One prim_index fetch answers both "is there a prim" and "what class models
        # it"; the composed typeName is then handed to Prim so it need not ask again.
        type_name = self._engine.resolve_view_type_name(path)
        if type_name is None:
            raise KeyError(path)

        return Prim(self, path, _type_name=type_name)

    def __setitem__(self, path: str, prim: PrimSpec) -> None:
        self.edit_layer[normalize_prim_path(path)] = prim
        self.invalidate()

    def __delitem__(self, path: str) -> None:
        del self.edit_layer[normalize_prim_path(path)]
        self.invalidate()

    def def_(self, prim_type: Type[PrimType], path: str) -> PrimType:
        self.edit_layer[normalize_prim_path(path)] = self._new_spec(prim_type, Specifier.Def)
        self.invalidate()
        # The prim was just defined as prim_type, but __getitem__ only promises Prim.
        return cast(PrimType, self[path])

    def class_(self, path: str) -> Prim:
        self.edit_layer[normalize_prim_path(path)] = self._new_spec(None, Specifier.Class)
        self.invalidate()
        return self[path]

    def over_(self, path: str) -> Prim:
        self.edit_layer[normalize_prim_path(path)] = self._new_spec(None, Specifier.Over)
        self.invalidate()
        return self[path]

    def _ensure_edit_prim(self, path: str) -> PrimSpec:
        path = normalize_prim_path(path)
        if path == "/":
            raise ValueError("cannot author the pseudo-root prim")

        prim = prim_at(self.edit_layer, path)
        if prim is not None:
            return prim

        self.edit_layer[path] = PrimSpec(specifier=Specifier.Over)
        prim = prim_at(self.edit_layer, path)
        if prim is None:
            raise RuntimeError(f"failed to create edit prim at {path}")

        return prim

    def _set_property(self, prim_path: str, prop_name: str, value: Any) -> PropertySpec:
        prim_path = normalize_prim_path(prim_path)
        prop_name = normalize_property_name(prop_name)
        template = self._engine.resolve_property(prim_path, prop_name)
        edit_prim = self._ensure_edit_prim(prim_path)

        if isinstance(value, PropertySpec):
            prop = value.clone()
            prop._name = prop_name.split(":")[-1]
            self._install_property(edit_prim, prop_name, prop)
            self.invalidate()
            return prop

        if isinstance(template, RelationshipSpec) or Relationship._is_relationship_value(value):
            rel = self._ensure_edit_relationship(edit_prim, prop_name, template)
            rel._targets = Relationship._coerce_relationship_targets(value)
            rel._value_state = PropertySpec.ValueState.Authored
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
    ) -> Property:
        edit_prim = self._ensure_edit_prim(prim_path)
        prop_name = normalize_property_name(prop_name)
        attr = AttributeSpec(
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
        attr._value_state = PropertySpec.ValueState.NotAuthored
        self._install_property(edit_prim, prop_name, attr)
        if value is not None:
            attr.set(value)
        self.invalidate()
        return Attribute(self, prim_path, prop_name)

    def _create_relationship(
        self,
        prim_path: str,
        prop_name: str,
        targets: Any = None,
        doc: str = "",
        metadata: Optional[dict] = None,
        custom: bool = True,
        is_leaf: bool = True,
    ) -> Property:
        edit_prim = self._ensure_edit_prim(prim_path)
        prop_name = normalize_property_name(prop_name)
        rel = RelationshipSpec(
            name=prop_name.split(":")[-1],
            doc=doc,
            metadata=metadata,
            custom=custom,
            is_leaf=is_leaf,
        )
        rel._value_state = PropertySpec.ValueState.NotAuthored
        if targets is not None:
            rel._targets = Relationship._coerce_relationship_targets(targets)
            rel._value_state = PropertySpec.ValueState.Authored
        self._install_property(edit_prim, prop_name, rel)
        self.invalidate()
        return Relationship(self, prim_path, prop_name)

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

    def _install_property(self, prim: PrimSpec, prop_name: str, prop: PropertySpec) -> PropertySpec:
        names = normalize_property_name(prop_name).split(":")
        current: Union[PrimSpec, PropertySpec] = prim
        for name in names[:-1]:
            props = current._props
            if name not in props:
                namespace_prop = PropertySpec(name, custom=True, is_leaf=False)
                current.create_prop(namespace_prop)
            current = props[name]

        prop._name = names[-1]
        current.create_prop(prop)
        return prop

    def _ensure_edit_property(
        self,
        prim: PrimSpec,
        prop_name: str,
        template: Optional[PropertySpec],
    ) -> PropertySpec:
        prop_name = normalize_property_name(prop_name)
        existing = self._local_prop_at(prim, prop_name)
        if existing is not None:
            return existing

        if template is not None:
            prop = self._clone_for_edit(template)
        else:
            prop = PropertySpec(prop_name.split(":")[-1], custom=True, is_leaf=False)

        return self._install_property(prim, prop_name, prop)

    def _ensure_edit_attribute(
        self,
        prim: PrimSpec,
        prop_name: str,
        template: Optional[PropertySpec],
        value: Any,
    ) -> AttributeSpec:
        existing = self._local_prop_at(prim, prop_name)
        if isinstance(existing, AttributeSpec):
            return existing

        if isinstance(template, AttributeSpec):
            attr = self._clone_for_edit(template)
            if not isinstance(attr, AttributeSpec):
                raise TypeError("template clone did not produce an AttributeSpec")
        else:
            value_type = str if value is None else infer_type(value)
            attr = AttributeSpec(value_type, prop_name.split(":")[-1], custom=True, fix_type=False)
            attr._value_state = PropertySpec.ValueState.NotAuthored

        self._install_property(prim, prop_name, attr)
        return attr

    def _ensure_edit_relationship(
        self,
        prim: PrimSpec,
        prop_name: str,
        template: Optional[PropertySpec],
    ) -> RelationshipSpec:
        existing = self._local_prop_at(prim, prop_name)
        if isinstance(existing, RelationshipSpec):
            return existing

        if isinstance(template, RelationshipSpec):
            rel = self._clone_for_edit(template)
            if not isinstance(rel, RelationshipSpec):
                raise TypeError("template clone did not produce a RelationshipSpec")
        else:
            rel = RelationshipSpec(prop_name.split(":")[-1], custom=True)
            rel._value_state = PropertySpec.ValueState.NotAuthored

        self._install_property(prim, prop_name, rel)
        return rel

    @staticmethod
    def _new_spec(prim_type: Optional[type], specifier: Specifier) -> PrimSpec:
        """Create plain storage for a prim, recording the type it was defined with.

        The schema class is only a type token here: it is never instantiated, and
        the resulting spec carries no materialised properties. Declarations are
        resolved later, against the registry, by typeName.
        """
        prim = PrimSpec(specifier=specifier)
        if prim_type is not None and prim_type.__name__ != "PrimSpec":
            prim._metadata._builtin_data["typeName"] = prim_type.__name__

        return prim

    @staticmethod
    def _clone_for_edit(prop: PropertySpec) -> PropertySpec:
        """A detached copy of a resolved property, ready to be authored over."""
        result = prop.clone()
        result._parent = None
        if isinstance(result, AttributeSpec):
            result._time_samples = {}
            result._value_state = PropertySpec.ValueState.NotAuthored
        elif isinstance(result, RelationshipSpec):
            result._targets = []
            result._value_state = PropertySpec.ValueState.NotAuthored
        else:
            result._value_state = PropertySpec.ValueState.NotAuthored

        return result

    @staticmethod
    def _local_prop_at(prim: PrimSpec, prop_name: str) -> Optional[PropertySpec]:
        """The property already authored on this spec, without consulting composition."""
        names = normalize_property_name(prop_name).split(":")
        current: Any = prim
        for name in names:
            if name not in current._props:
                return None

            current = current._props[name]

        return current
