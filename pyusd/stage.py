"""Stage: a composed view over a root layer, and the edit target that authors it.

The prim view lives in :mod:`pyusd.prim`; property, metadata, and variant views in
their own modules. This module holds the stage itself plus the plumbing that
writes opinions into the edit layer.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union, cast

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
    infer_type,
    join_relative_path,
    normalize_prim_path,
    normalize_property_name,
    path_items,
    prim_at,
)

# Metadata a flattened prim must not carry. The specifier and typeName are written
# in the prim header; the arcs are inlined by the flattening itself (references,
# inherits and payloads contribute their opinions directly, relocates are applied,
# variants are resolved into plain children), so carrying them would ask the reader
# to compose the same opinions a second time, from files the flattened text no
# longer mentions.
_FLATTEN_SKIPPED_PRIM_METADATA = frozenset({
    "specifier",
    "typeName",
    "inherits",
    "references",
    "payloads",
    "specializes",
    "variantSets",
    "variants",
})


class Stage:
    root_layer: Layer
    edit_layer: Layer
    layer_cache: LayerCache
    _engine: CompositionEngine
    prim_views: Dict[Tuple[str, type], Prim]
    _variant_edit_target: Optional[Tuple[str, PrimSpec]]
    _variant_edit_target_stack: List[Tuple[str, PrimSpec]]

    def __init__(
        self,
        root_layer: Union[str, Layer] = "",
        edit_layer: Optional[Layer] = None,
        new: bool = False,
    ) -> None:
        if isinstance(root_layer, Layer):
            # A layer handed in already decided for itself; `new` says nothing about a
            # Layer, so it is only about the file-name form below.
            resolved_root = root_layer
        elif new:
            # Asked into existence, so do not consult the registry, do not look at the
            # filesystem, and do not parse. The flag goes on the layer, which is what
            # LayerCache.materialize reads to keep the lazy path from loading either.
            resolved_root = Layer(str(root_layer), new=True)
        else:
            file_name = str(root_layer)
            resolved_root = Layer._lookup(file_name)
            if resolved_root is None:
                if file_name and os.path.exists(Layer._registry_key(file_name)):
                    resolved_root = Layer.load(file_name)
                else:
                    resolved_root = Layer(file_name)

        # The per-stage state lives directly on the stage: unlike Layer, a Stage is
        # never interned or shared, so there is no wrapper/impl split to maintain --
        # one stage, one engine, one cache, one view table.
        self.root_layer = resolved_root
        self.edit_layer = edit_layer or resolved_root
        self.layer_cache = LayerCache()
        self._engine = CompositionEngine(resolved_root, self.layer_cache)
        # One Prim view per (path, class), so asking a stage for the same path twice
        # hands back the same object. Keying on the class rather than the path alone
        # is what keeps this correct without an invalidation hook: the class comes from
        # the composed typeName, so a stronger layer that retypes a prim lands on a
        # different key and the stale view is never handed out again. It stays in the
        # dict, unreferenced by anything but itself.
        self.prim_views: Dict[Tuple[str, type], Prim] = {}
        # No variant edit context until one is entered; the stack makes nesting
        # work, which a single slot would not.
        self._variant_edit_target: Optional[Tuple[str, PrimSpec]] = None
        self._variant_edit_target_stack: List[Tuple[str, PrimSpec]] = []

    def __iter__(self):
        return self.traverse()

    @staticmethod
    def open(file_name: str) -> Stage:
        return Stage(file_name)

    def save(self, file_name: str = "") -> None:
        """Save the root layer; ``file_name`` relocates it, as ``Layer.save`` does."""
        self.root_layer.save(file_name)

    def to_str(self) -> str:
        """USDA text of the fully composed stage, flattened.

        pxr spells this ``UsdStage.ExportToString``. A fresh anonymous layer is
        assembled from the composed result and serialized: every populated prim
        contributes its strongest specifier and typeName, its composed metadata,
        and the strongest opinion for every property any contributing spec
        authored. Nothing survives that the composed stage does not answer for --
        schema-declared fallbacks are not opinions and do not appear -- so parsing
        the text back builds a stage that answers the same values as this one,
        with no arc left to resolve.
        """
        flat = Layer()
        self._flatten_layer_metadata(flat)
        for name in self.child_names("/"):
            flat.add_root_prim(self._flatten_prim(join_relative_path("/", name)))

        return flat.to_str()

    def _flatten_layer_metadata(self, flat: Layer) -> None:
        keys: List[str] = []
        seen: Set[str] = set()
        for layer in self._engine.layer_stack(self.root_layer):
            metadata = layer.metadata
            for key, is_set in metadata._builtin_is_set.items():
                if is_set and key not in seen:
                    seen.add(key)
                    keys.append(key)

            for key in metadata._custom_data:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)

        for key in keys:
            if key in ("subLayers", "relocates"):
                # Composition arcs, not scene content: flattening is what removes them.
                continue

            value = self._engine.resolve_metadata(None, key)
            if value is None:
                continue

            setattr(flat.metadata, key, value)

    def _flatten_prim(self, path: str) -> PrimSpec:
        engine = self._engine
        path = normalize_prim_path(path)
        index = engine.prim_index(path)
        name = path_items(path)[-1] if path_items(path) else ""
        spec = PrimSpec(name=name, specifier=self._composed_specifier(index))

        if index.type_name:
            spec._metadata._builtin_data["typeName"] = index.type_name

        self._flatten_prim_metadata(path, spec)

        names: List[str] = []
        seen: Set[str] = set()
        for source in index.specs:
            for prop_name in engine._flatten_property_names(source.prim._props.values()):
                engine._append_name(names, seen, prop_name)

        for prop_name in names:
            resolved = engine.resolve_property(path, prop_name)
            if resolved is None or resolved.value_state == PropertySpec.ValueState.Fallback:
                continue

            prop = resolved.clone()
            self._flatten_property_metadata(path, prop_name, prop)
            self._install_property(spec, prop_name, prop)

        for child_name in engine.child_names(path):
            spec.add_child(self._flatten_prim(join_relative_path(path, child_name)))

        return spec

    @staticmethod
    def _composed_specifier(index: Any) -> Specifier:
        """The composed specifier, by specifier kind rather than layer strength.

        pxr composes specifiers as def > class > over across all contributing
        specs, so an over that references (or inherits) a def composes to def --
        that is what makes a flattened reference chain read as plain defs instead
        of the overs the editing layer authored. Layer strength plays no part:
        an over in the strongest layer does not drag a def in a weaker one back
        down to over.
        """
        specifier = Specifier.Over
        for source in index.specs:
            source_specifier = source.prim.specifier
            if source_specifier == Specifier.Def:
                return Specifier.Def

            if source_specifier == Specifier.Class:
                specifier = Specifier.Class

        return specifier

    def _flatten_prim_metadata(self, path: str, spec: PrimSpec) -> None:
        keys: List[str] = []
        seen: Set[str] = set()
        for source in self._engine.prim_index(path).specs:
            metadata = source.prim._metadata
            for key, is_set in metadata._builtin_is_set.items():
                if is_set and key not in seen:
                    seen.add(key)
                    keys.append(key)

            for key in metadata._custom_data:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)

        for key in keys:
            if key in _FLATTEN_SKIPPED_PRIM_METADATA:
                continue

            value = self._engine.resolve_metadata(path, key)
            if value is None:
                continue

            setattr(spec._metadata, key, value)

    def _flatten_property_metadata(
        self,
        path: str,
        prop_name: str,
        prop: PropertySpec,
    ) -> None:
        keys: List[str] = []
        seen: Set[str] = set()
        for source in self._engine.property_specs(path, prop_name):
            metadata = source._metadata
            for key, is_set in metadata._builtin_is_set.items():
                if is_set and key not in seen:
                    seen.add(key)
                    keys.append(key)

            for key in metadata._custom_data:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)

        for key in keys:
            value = self._engine.resolve_metadata(path, key, prop_name)
            if value is None:
                continue

            setattr(prop._metadata, key, value)

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

    @default_prim.setter
    def default_prim(self, value: Union[Prim, PrimSpec, str]) -> None:
        """Author ``defaultPrim`` in the edit layer.

        The read side always existed and the write side did not, so the only way in was
        ``stage.metadata.defaultPrim``. A property that can be read but not assigned is
        an asymmetry rather than a decision -- and it was the one thing the referencing
        example could not do. pxr spells this ``SetDefaultPrim`` and takes a ``Usd.Prim``.

        A prim belonging to another stage is rejected rather than ignored. pxr leaves
        the existing opinion alone in that case, which is safe but silent, and here it
        would read as a successful assignment of something that is not on this stage.
        """
        from .prim import Prim as _Prim

        if isinstance(value, _Prim):
            if value.stage is not self:
                raise ValueError(
                    f"cannot make {value.path} the default prim of a stage it does not "
                    "belong to"
                )

            path = value.path
        elif isinstance(value, PrimSpec):
            path = value.path
        elif isinstance(value, str):
            path = value
        else:
            raise TypeError(
                "default_prim must be a Prim, a PrimSpec or a path string, not "
                f"{type(value).__name__}"
            )

        if not path.startswith("/"):
            path = "/" + path

        # defaultPrim carries the prim NAME: pxr writes `defaultPrim = "hello"`,
        # not the path spelling, so authoring here has to match or every layer
        # this stage saves diverges from what pxr itself would have written.
        self.metadata.defaultPrim = path.lstrip("/")

    def invalidate(self) -> None:
        self._engine.clear()

    @property
    def variant_edit_target(self) -> Optional[Tuple[str, PrimSpec]]:
        """The variant an edit context is writing into, or None outside one.

        Held as the stage path of the owning prim together with that prim's
        variant spec. A variant's content has no absolute stage path of its own,
        so this is what lets a write aimed at ``/hello/world`` land on the prim
        the variant calls ``world``: the target's path is the prefix every
        authored path is resolved against, and the spec is where the lookup
        actually happens.

        Composed reads are untouched by it, which is the point -- ``with``
        changes where a write lands, not what the stage reports.
        """
        return self._variant_edit_target

    def _push_variant_edit_target(self, prim_path: str, variant: PrimSpec) -> None:
        self._variant_edit_target_stack.append((prim_path, variant))
        self._variant_edit_target = (prim_path, variant)

    def _pop_variant_edit_target(self) -> None:
        if not self._variant_edit_target_stack:
            return

        self._variant_edit_target_stack.pop()
        self._variant_edit_target = (
            self._variant_edit_target_stack[-1] if self._variant_edit_target_stack
            else None
        )

    def _resolve_edit_target_path(self, path: str) -> Optional[str]:
        """``path`` relative to the active variant, or None when it is not under it.

        A path outside the variant's prim has no meaning inside it, so this
        answers None rather than inventing a location for it.
        """
        if self._variant_edit_target is None:
            return None

        root, _ = self._variant_edit_target
        if path == root:
            return ""

        prefix = root + "/"
        if not path.startswith(prefix):
            return None

        return path[len(prefix):]

    def _edit_target_property(
        self, prim_path: str, prop_name: str
    ) -> Optional[PropertySpec]:
        """The property as the active variant stores it, or None.

        None means "read this one the usual way": either there is no edit
        context, or the prim is not inside the variant being edited. It also
        covers a prim the variant does not mention, since an opinion that is not
        there has nothing to read and the composed value is the right answer.
        """
        relative = self._resolve_edit_target_path(normalize_prim_path(prim_path))
        if relative is None:
            return None

        target = self._variant_edit_target
        if target is None:
            return None

        variant = target[1]
        if relative == "":
            spec = variant
        else:
            spec = variant
            for item in relative.split("/"):
                if item not in spec._children:
                    return None

                spec = spec._children[item]

        return self._engine._prop_at(spec, normalize_property_name(prop_name))

    def has_prim(self, path: str) -> bool:
        return self._engine.has_prim(path)

    def get_prim_at_path(self, path: str) -> Optional[Prim]:
        """The prim view at ``path``, or None when it is not populated.

        pxr's ``GetPrimAtPath``: the answering form of the question
        :meth:`has_prim` asks. ``__getitem__`` cannot be it, because a missing
        prim has to raise ``KeyError`` there -- a stage lookup that guesses is
        worse than one that says no, and :attr:`default_prim` above needed
        exactly this shape.
        """
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

    def traverse(self, path: str = "/", all: bool = False) -> Iterable[Prim]:
        """Yield the composed prims beneath ``path``, depth first.

        With ``all`` False (the default) this is pxr's ``Traverse``: a prim whose
        composed ``active`` metadata is False is skipped together with everything
        beneath it. With ``all`` True this is ``TraverseAll``: every prim is
        visited. The composition engine itself stays active-blind -- inactive
        prims remain composed and reachable by explicit path either way -- so
        deactivation is a traversal-time decision here, not a composition one.
        """
        path = normalize_prim_path(path)
        if path != "/":
            if not all and not self._is_active_prim(path):
                return

            yield self[path]

        for child_name in self.child_names(path):
            child_path = join_relative_path(path, child_name)
            yield from self.traverse(child_path, all)

    def _is_active_prim(self, path: str) -> bool:
        """The composed ``active`` opinion; nothing authored means active."""
        return self._engine.resolve_metadata(path, "active") is not False

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

        # Inside a variant edit context a write aimed at a stage path lands on
        # the prim the variant calls by that name. The spec has to be an over
        # carrying the type the path composes as, or an attribute written here
        # has no type to infer from and falls back to tuple[] plus custom --
        # which is what authoring through the variant's own spec already does.
        target = self._variant_edit_target
        variant_path = self._resolve_edit_target_path(path)
        if target is not None and variant_path is not None:
            variant = target[1]
            if variant_path == "":
                return variant

            relative = variant_path.split("/")

            existing = variant
            for item in relative[:-1]:
                existing = existing._children[item]

            name = relative[-1]
            prim = existing._children.get(name)
            if prim is None:
                prim = PrimSpec(name, specifier=Specifier.Over)
                existing[name] = prim
                # An over authored inside a variant composes as whatever the
                # stage calls it at that path, so record that type: it is what
                # lets an attribute written here infer its own type instead of
                # falling back to tuple[] with a custom prefix.
                resolved = self._engine.resolve_type_name(path)
                if resolved:
                    prim._metadata._builtin_data["typeName"] = resolved

            return prim

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

        # An augmented assignment assigns its result back, so `prim.radius += 1`
        # finishes by storing the handle that __iadd__ returned, and a plain
        # `prim.radius = other.radius` hands over a handle too. Neither is asking
        # to author a handle, so unwrap to the value the handle stands for. A
        # Relationship unwraps to its targets, which then route to the relationship
        # branch below like any other path list.
        if isinstance(value, Property):
            value = value._value()

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
