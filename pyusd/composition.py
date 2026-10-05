from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from .layer import Layer, LayerImpl
from .prim_spec import PrimSpec
from .property_spec import PropertySpec
from .sdf import Specifier
from .utils import (
    ancestors,
    join_path,
    normalize_prim_path,
    normalize_property_name,
    path_from_reference_text,
    path_is_under,
    path_items,
    path_suffix,
    prim_at,
    prim_descendant,
)


class ArcType(Enum):
    LOCAL = "local"
    INHERITS = "inherits"
    VARIANTS = "variants"
    RELOCATES = "relocates"
    REFERENCES = "references"
    PAYLOADS = "payloads"
    SPECIALIZES = "specializes"


@dataclass(frozen=True)
class ArcTarget:
    layer: Layer
    path: str


@dataclass(frozen=True)
class SourcePrimSpec:
    prim: PrimSpec
    layer: Layer
    composed_path: str
    source_path: str
    arc_type: ArcType

    def with_arc_type(self, arc_type: ArcType, composed_path: str) -> SourcePrimSpec:
        return SourcePrimSpec(
            prim=self.prim,
            layer=self.layer,
            composed_path=composed_path,
            source_path=self.source_path,
            arc_type=arc_type,
        )


@dataclass
class PrimIndex:
    path: str
    specs: List[SourcePrimSpec]

    @property
    def strongest_spec(self) -> Optional[SourcePrimSpec]:
        if not self.specs:
            return None

        return self.specs[0]

    @property
    def type_name(self) -> str:
        """Composed typeName, strongest opinion first; empty when untyped."""
        for spec in self.specs:
            value = spec.prim._metadata._builtin_data.get("typeName")
            if value:
                return str(value)

        return ""


class LayerCache:
    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[Optional[float], Optional[int], Layer]] = {}

    def load(self, file_name: str, anchor_file: str = "") -> Layer:
        abs_path = self.resolve_path(file_name, anchor_file)
        try:
            stat = os.stat(abs_path)
            signature = (stat.st_mtime, stat.st_size)
        except OSError:
            signature = (None, None)

        cached = self._cache.get(abs_path)
        if cached is not None and cached[0] == signature[0] and cached[1] == signature[1]:
            return cached[2]

        layer = Layer.load(abs_path)
        self._cache[abs_path] = (signature[0], signature[1], layer)
        return layer

    def resolve_path(self, file_name: str, anchor_file: str = "") -> str:
        file_name = str(file_name).strip("@")
        if os.path.isabs(file_name):
            return os.path.abspath(file_name).replace("\\", "/")

        if anchor_file:
            base_dir = os.path.dirname(os.path.abspath(anchor_file))
            return os.path.abspath(os.path.join(base_dir, file_name)).replace("\\", "/")

        return os.path.abspath(file_name).replace("\\", "/")

    def materialize(self, layer: Layer, anchor_file: str = "") -> Layer:
        if not layer.file_name:
            return layer

        # A layer created with new=True is never filled from disk. This has to be
        # checked here and not only where the root layer is built: materializing is
        # the lazy path, so a Layer("out.usda", new=True) would otherwise come back
        # with the file's contents on the first prim query, long after the caller
        # said not to read it.
        if layer._is_new:
            return layer

        abs_path = self.resolve_path(layer.file_name, anchor_file)
        has_authored_content = bool(layer._root_prims or layer._sub_layers)
        if layer._default_prim_name:
            has_authored_content = True

        if not has_authored_content and os.path.exists(abs_path):
            return self.load(layer.file_name, anchor_file)

        return layer

    def invalidate(self, file_name: str = "") -> None:
        if not file_name:
            self._cache.clear()
            return

        abs_path = os.path.abspath(file_name).replace("\\", "/")
        self._cache.pop(abs_path, None)


class CompositionEngine:
    _ASSET_ARC_RE = re.compile(r"^@([^@]*)@(.*)$")
    _PRIM_PATH_RE = re.compile(r"<([^>]*)>")

    def __init__(self, root_layer: Layer, layer_cache: Optional[LayerCache] = None) -> None:
        self.root_layer = root_layer
        self.layer_cache = layer_cache or LayerCache()
        self.load_payloads = True
        self.unloaded_payloads: Set[str] = set()
        self._prim_index_cache: Dict[
            Tuple[int, str, bool, Tuple[str, ...], Tuple[Tuple[int, int], ...]],
            PrimIndex,
        ] = {}
        self._layer_stack_cache: Dict[
            int, Tuple[Tuple[Tuple[int, int], ...], List[Layer]]
        ] = {}
        self._seen_revision = LayerImpl.global_revision

    def clear(self) -> None:
        self._prim_index_cache.clear()
        self._layer_stack_cache.clear()

    def prim_index(self, path: str, root_layer: Optional[Layer] = None) -> PrimIndex:
        if self._seen_revision != LayerImpl.global_revision:
            self.clear()
            self._seen_revision = LayerImpl.global_revision

        root_layer = root_layer or self.root_layer
        path = normalize_prim_path(path)
        payload_key = tuple(sorted(self.unloaded_payloads))
        layer_signature = tuple(
            (id(layer._impl), layer.revision)
            for layer in self.layer_stack(root_layer)
        )
        key = (id(root_layer), path, self.load_payloads, payload_key, layer_signature)
        if key not in self._prim_index_cache:
            self._prim_index_cache[key] = self._build_prim_index(root_layer, path, set())

        return self._prim_index_cache[key]

    def has_prim(self, path: str, root_layer: Optional[Layer] = None) -> bool:
        path = normalize_prim_path(path)
        if path == "/":
            return True

        return bool(self.prim_index(path, root_layer).specs)

    def resolve_view_type_name(
        self, path: str, root_layer: Optional[Layer] = None
    ) -> Optional[str]:
        """Composed typeName at ``path``, or None when there is no prim there.

        A composed view needs both answers at once -- does the prim exist, and what
        class models it -- and ``has_prim`` plus ``resolve_type_name`` each fetch the
        prim index to give one of them. That is not a cheap fetch twice over: every
        ``prim_index`` call rebuilds a cache key holding a signature of the whole layer
        stack and a sorted list of unloaded payloads. Answering both from one index
        halves the cost of a view lookup.
        """
        path = normalize_prim_path(path)
        if path == "/":
            return ""

        specs = self.prim_index(path, root_layer).specs
        if not specs:
            return None

        return PrimIndex(path, specs).type_name

    def is_populated(self, path: str, root_layer: Optional[Layer] = None) -> bool:
        """A path joins the namespace only when some contributing spec is a def.

        over and class specs supply opinions but never create a prim, so they
        are reachable by explicit path yet absent from child enumeration.
        """
        path = normalize_prim_path(path)
        if path == "/":
            return True

        for spec in self.prim_index(path, root_layer).specs:
            if spec.prim.specifier == Specifier.Def:
                return True

        return False

    def child_names(self, path: str, root_layer: Optional[Layer] = None) -> List[str]:
        root_layer = root_layer or self.root_layer
        path = normalize_prim_path(path)
        names: List[str] = []
        seen: Set[str] = set()

        if path == "/":
            for layer in reversed(self.layer_stack(root_layer)):
                for name in layer._root_prims:
                    prim_path = "/" + name
                    if self._is_relocated_source_path(root_layer, prim_path):
                        continue
                    self._append_populated_name(names, seen, prim_path, root_layer)

                for _, dest in self._iter_relocates(layer):
                    dest_path = normalize_prim_path(dest)
                    root_name = path_items(dest_path)[0] if path_items(dest_path) else ""
                    if root_name:
                        self._append_populated_name(
                            names, seen, "/" + root_name, root_layer
                        )
            return names

        for spec in reversed(self.prim_index(path, root_layer).specs):
            for name in spec.prim._children:
                self._append_populated_name(
                    names, seen, join_path(path, name), root_layer
                )

            for variant_set in spec.prim._variant_sets.values():
                selected = variant_set.selected_variant
                if selected is None:
                    continue

                for name in selected._children:
                    self._append_populated_name(
                        names, seen, join_path(path, name), root_layer
                    )

        return names

    def _append_populated_name(
        self,
        names: List[str],
        seen: Set[str],
        prim_path: str,
        root_layer: Optional[Layer],
    ) -> None:
        name = path_items(prim_path)[-1]
        if name in seen:
            return

        if not self.is_populated(prim_path, root_layer):
            return

        self._append_name(names, seen, name)

    def resolve_type_name(self, path: str, root_layer: Optional[Layer] = None) -> str:
        """Composed typeName of the prim at ``path``, strongest opinion first."""
        path = normalize_prim_path(path)
        if path == "/":
            return ""

        return self.prim_index(path, root_layer).type_name

    def resolve_property(self, path: str, prop_name: str, root_layer: Optional[Layer] = None) -> Optional[PropertySpec]:
        path = normalize_prim_path(path)
        prop_name = normalize_property_name(prop_name)
        fallback: Optional[PropertySpec] = None

        for spec in self.prim_index(path, root_layer).specs:
            prop = self._prop_at(spec.prim, prop_name)
            if prop is None:
                continue

            if prop.value_state == PropertySpec.ValueState.Cleared:
                return prop

            if prop.value_state == PropertySpec.ValueState.Authored:
                return prop

            if fallback is None:
                fallback = prop

        if fallback is not None:
            return fallback

        # Schema fallback: the composed type declares this property even when no
        # layer authored it, which is what gives a new attribute its value type.
        from . import schema_registry

        return schema_registry.declared_prop(
            self.resolve_type_name(path, root_layer), prop_name
        )

    def property_specs(self, path: str, prop_name: str, root_layer: Optional[Layer] = None) -> List[PropertySpec]:
        result: List[PropertySpec] = []
        path = normalize_prim_path(path)
        prop_name = normalize_property_name(prop_name)
        for spec in self.prim_index(path, root_layer).specs:
            prop = self._prop_at(spec.prim, prop_name)
            if prop is not None:
                result.append(prop)

        return result

    def property_names(self, path: str, root_layer: Optional[Layer] = None) -> List[str]:
        result: List[str] = []
        seen: Set[str] = set()
        for spec in self.prim_index(path, root_layer).specs:
            for name in self._flatten_property_names(spec.prim._props.values()):
                self._append_name(result, seen, name)

        from . import schema_registry

        for name in schema_registry.declared_leaf_names(
            self.resolve_type_name(path, root_layer)
        ):
            self._append_name(result, seen, name)

        return result

    def resolve_metadata(
        self,
        path: Optional[str],
        key: str,
        prop_name: str = "",
        root_layer: Optional[Layer] = None,
    ) -> Any:
        root_layer = root_layer or self.root_layer
        if path is None:
            return self._resolve_layer_metadata(root_layer, key)

        path = normalize_prim_path(path)
        if prop_name:
            return self._resolve_property_metadata(root_layer, path, prop_name, key)

        return self._resolve_prim_metadata(root_layer, path, key)

    def layer_stack(self, root_layer: Layer) -> List[Layer]:
        if self._seen_revision != LayerImpl.global_revision:
            self.clear()
            self._seen_revision = LayerImpl.global_revision

        key = id(root_layer)
        cached = self._layer_stack_cache.get(key)
        if cached is not None:
            signature, result = cached
            if signature == self._layer_signature(result):
                return result

        result = []
        self._collect_layer_stack(root_layer, result, set())
        self._layer_stack_cache[key] = (self._layer_signature(result), result)

        return result

    @staticmethod
    def _layer_signature(layer_stack: Iterable[Layer]) -> Tuple[Tuple[int, int], ...]:
        return tuple((id(layer._impl), layer.revision) for layer in layer_stack)

    def resolve_arc_target(self, arc: Any, owner_layer: Layer) -> Optional[ArcTarget]:
        if isinstance(arc, PrimSpec):
            if arc.layer is None:
                return None

            return ArcTarget(self.layer_cache.materialize(arc.layer), normalize_prim_path(arc.path))

        if isinstance(arc, Layer):
            layer = self.layer_cache.materialize(arc, owner_layer.file_name)
            return ArcTarget(layer, self._default_target_path(layer))

        text = str(arc).strip()
        if not text:
            return None

        asset_match = self._ASSET_ARC_RE.match(text)
        if asset_match:
            asset_path = asset_match.group(1)
            rest = asset_match.group(2).strip()
            layer = self.layer_cache.load(asset_path, owner_layer.file_name)
            target_path = self._path_from_arc_tail(rest) or self._default_target_path(layer)
            return ArcTarget(layer, target_path)

        target_path = self._path_from_arc_tail(text)
        if target_path:
            return ArcTarget(owner_layer, target_path)

        if text.startswith("/"):
            return ArcTarget(owner_layer, normalize_prim_path(text))

        if text.startswith("@") and text.endswith("@"):
            layer = self.layer_cache.load(text.strip("@"), owner_layer.file_name)
            return ArcTarget(layer, self._default_target_path(layer))

        return None

    def _build_prim_index(
        self,
        root_layer: Layer,
        path: str,
        stack: Set[Tuple[int, str]],
    ) -> PrimIndex:
        key = (id(root_layer), path)
        if key in stack:
            return PrimIndex(path, [])

        next_stack = set(stack)
        next_stack.add(key)

        specs: List[SourcePrimSpec] = []
        specs.extend(self._collect_local_specs(root_layer, path, ArcType.LOCAL))
        specs.extend(self._collect_composition_arcs(root_layer, path, "_inherits", ArcType.INHERITS, next_stack))
        specs.extend(self._collect_variant_specs(root_layer, path))
        specs.extend(self._collect_relocate_specs(root_layer, path))
        specs.extend(self._collect_composition_arcs(root_layer, path, "_references", ArcType.REFERENCES, next_stack))
        specs.extend(self._collect_composition_arcs(root_layer, path, "_payloads", ArcType.PAYLOADS, next_stack))
        specs.extend(self._collect_composition_arcs(root_layer, path, "_specializes", ArcType.SPECIALIZES, next_stack))

        return PrimIndex(path, specs)

    def _collect_local_specs(
        self,
        root_layer: Layer,
        path: str,
        arc_type: ArcType,
        allow_relocated_sources: bool = False,
    ) -> List[SourcePrimSpec]:
        path = normalize_prim_path(path)
        if path == "/":
            return []

        if not allow_relocated_sources and self._is_relocated_source_path(root_layer, path):
            return []

        specs: List[SourcePrimSpec] = []
        for layer in self.layer_stack(root_layer):
            prim = prim_at(layer, path)
            if prim is None:
                continue

            specs.append(SourcePrimSpec(prim, layer, path, prim.path, arc_type))

        return specs

    def _collect_composition_arcs(
        self,
        root_layer: Layer,
        path: str,
        attr_name: str,
        arc_type: ArcType,
        stack: Set[Tuple[int, str]],
    ) -> List[SourcePrimSpec]:
        path = normalize_prim_path(path)
        specs: List[SourcePrimSpec] = []
        for owner_path in ancestors(path):
            if attr_name == "_payloads" and not self._is_payload_loaded(owner_path):
                continue

            suffix = path_suffix(owner_path, path)
            for owner_spec in self._arc_owner_specs(root_layer, owner_path):
                arcs = getattr(owner_spec.prim, attr_name)
                for arc in arcs:
                    target = self.resolve_arc_target(arc, owner_spec.layer)
                    if target is None:
                        continue

                    target_path = join_path(target.path, suffix)
                    target_index = self._build_prim_index(target.layer, target_path, stack)
                    for target_spec in target_index.specs:
                        specs.append(target_spec.with_arc_type(arc_type, path))

        return specs

    def _collect_variant_specs(self, root_layer: Layer, path: str) -> List[SourcePrimSpec]:
        path = normalize_prim_path(path)
        specs: List[SourcePrimSpec] = []
        for owner_path in ancestors(path):
            suffix = path_suffix(owner_path, path)
            for owner_spec in self._collect_local_specs(root_layer, owner_path, ArcType.LOCAL):
                for variant_set in owner_spec.prim._variant_sets.values():
                    selected = variant_set.selected_variant
                    if selected is None:
                        continue

                    variant_prim = prim_descendant(selected, suffix)
                    if variant_prim is None:
                        continue

                    specs.append(
                        SourcePrimSpec(
                            variant_prim,
                            owner_spec.layer,
                            path,
                            variant_prim.path,
                            ArcType.VARIANTS,
                        )
                    )

        return specs

    def _collect_relocate_specs(self, root_layer: Layer, path: str) -> List[SourcePrimSpec]:
        path = normalize_prim_path(path)
        specs: List[SourcePrimSpec] = []
        for layer in self.layer_stack(root_layer):
            for source, dest in self._iter_relocates(layer):
                source_path = normalize_prim_path(source)
                dest_path = normalize_prim_path(dest)
                if not path_is_under(path, dest_path):
                    continue

                suffix = path_suffix(dest_path, path)
                relocated_source_path = join_path(source_path, suffix)
                specs.extend(
                    self._collect_local_specs(
                        layer,
                        relocated_source_path,
                        ArcType.RELOCATES,
                        allow_relocated_sources=True,
                    )
                )

        return [
            SourcePrimSpec(spec.prim, spec.layer, path, spec.source_path, ArcType.RELOCATES)
            for spec in specs
        ]

    def _arc_owner_specs(self, root_layer: Layer, owner_path: str) -> List[SourcePrimSpec]:
        specs: List[SourcePrimSpec] = []
        specs.extend(self._collect_local_specs(root_layer, owner_path, ArcType.LOCAL))
        specs.extend(self._collect_variant_specs(root_layer, owner_path))
        specs.extend(self._collect_relocate_specs(root_layer, owner_path))
        return specs

    def _collect_layer_stack(self, layer: Layer, result: List[Layer], seen: Set[str]) -> None:
        layer = self.layer_cache.materialize(layer)
        layer_id = layer.id()
        if layer_id in seen:
            return

        seen.add(layer_id)
        result.append(layer)
        materialized_sub_layers = []
        for sub_layer in layer._sub_layers:
            materialized = self.layer_cache.materialize(sub_layer, layer.file_name)
            materialized_sub_layers.append(materialized)
            self._collect_layer_stack(materialized, result, seen)
        layer._sub_layers = materialized_sub_layers

    def _resolve_layer_metadata(self, root_layer: Layer, key: str) -> Any:
        fallback = None
        for layer in self.layer_stack(root_layer):
            metadata = layer.metadata
            if key in metadata._builtin_data:
                if fallback is None:
                    fallback = metadata._builtin_data[key]
                if metadata._builtin_is_set.get(key, False):
                    return metadata._builtin_data[key]
            elif key in metadata._custom_data and metadata._custom_is_set.get(key, False):
                return metadata._custom_data[key]

        return fallback

    def _resolve_prim_metadata(self, root_layer: Layer, path: str, key: str) -> Any:
        values: List[Any] = []
        fallback = None
        for spec in self.prim_index(path, root_layer).specs:
            metadata = spec.prim.metadata
            if key in metadata._builtin_data:
                value = metadata._builtin_data[key]
                if fallback is None:
                    fallback = value
                if metadata._builtin_is_set.get(key, False):
                    if isinstance(value, dict):
                        values.append(value)
                    else:
                        return value
            elif key in metadata._custom_data and metadata._custom_is_set.get(key, False):
                value = metadata._custom_data[key]
                if isinstance(value, dict):
                    values.append(value)
                else:
                    return value

        if values:
            return self._compose_dictionaries(values)

        return fallback

    def _resolve_property_metadata(
        self,
        root_layer: Layer,
        path: str,
        prop_name: str,
        key: str,
    ) -> Any:
        values: List[Any] = []
        fallback = None
        for prop in self.property_specs(path, prop_name, root_layer):
            metadata = prop.metadata
            if key in metadata._builtin_data:
                value = metadata._builtin_data[key]
                if fallback is None:
                    fallback = value
                if metadata._builtin_is_set.get(key, False):
                    if isinstance(value, dict):
                        values.append(value)
                    else:
                        return value
            elif key in metadata._custom_data and metadata._custom_is_set.get(key, False):
                value = metadata._custom_data[key]
                if isinstance(value, dict):
                    values.append(value)
                else:
                    return value

        if values:
            return self._compose_dictionaries(values)

        return fallback

    def _iter_relocates(self, layer: Layer) -> Iterable[Tuple[str, str]]:
        for source, dest in layer._relocates.items():
            source_path = source.path if isinstance(source, PrimSpec) else str(source)

            yield path_from_reference_text(source_path), path_from_reference_text(str(dest))

    def _is_relocated_source_path(self, root_layer: Layer, path: str) -> bool:
        path = normalize_prim_path(path)
        for layer in self.layer_stack(root_layer):
            for source, _ in self._iter_relocates(layer):
                if path_is_under(path, normalize_prim_path(source)):
                    return True

        return False

    def _is_payload_loaded(self, owner_path: str) -> bool:
        if not self.load_payloads:
            return False

        owner_path = normalize_prim_path(owner_path)
        return owner_path not in self.unloaded_payloads

    def _default_target_path(self, layer: Layer) -> str:
        if layer.default_prim is not None:
            return normalize_prim_path(layer.default_prim.path)

        if len(layer._root_prims) == 1:
            return "/" + next(iter(layer._root_prims.keys()))

        return "/"

    def _path_from_arc_tail(self, text: str) -> str:
        match = self._PRIM_PATH_RE.search(text)
        if match:
            return normalize_prim_path(match.group(1))

        if text.startswith("<") and text.endswith(">"):
            return normalize_prim_path(text[1:-1])

        return ""

    @staticmethod
    def _append_name(names: List[str], seen: Set[str], name: str) -> None:
        if name in seen:
            return

        seen.add(name)
        names.append(name)

    @staticmethod
    def _prop_at(prim: PrimSpec, prop_name: str) -> Optional[PropertySpec]:
        names = normalize_property_name(prop_name).split(":")
        if not names or not names[0]:
            return None

        current: Any = prim
        for name in names:
            props = getattr(current, "_props", {})
            if name not in props:
                return None

            current = props[name]

        return current

    @staticmethod
    def _flatten_property_names(
        props: Iterable[PropertySpec], prefix: str = ""
    ) -> Iterable[str]:
        for prop in props:
            name = prop.name if not prefix else f"{prefix}:{prop.name}"
            if not prop.is_leaf and prop._props:
                # Namespace properties organise children; they are not properties
                # themselves and must not show up in property enumeration.
                yield from CompositionEngine._flatten_property_names(
                    prop._props.values(), name
                )
                continue

            yield name
            yield from CompositionEngine._flatten_property_names(
                prop._props.values(), name
            )

    @staticmethod
    def _deep_update(target: Dict[Any, Any], value: Dict[Any, Any]) -> None:
        for key, sub_value in value.items():
            if isinstance(sub_value, dict) and isinstance(target.get(key), dict):
                CompositionEngine._deep_update(target[key], sub_value)
            else:
                target[key] = sub_value

    @classmethod
    def _compose_dictionaries(cls, values: List[Dict[Any, Any]]) -> Dict[Any, Any]:
        result: Dict[Any, Any] = {}
        for value in reversed(values):
            cls._deep_update(result, value)

        return result
