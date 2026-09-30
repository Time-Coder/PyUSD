"""Variant set authoring for a composed prim.

A prim inside a variant has no absolute stage path, so it cannot be a
``(stage, path)`` view. Authoring therefore stays on the spec, reached through the
prim's edit target, while reading variant content goes through the stage
(``stage["/Model/high"]``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Optional

from .prim_spec import PrimSpec

if TYPE_CHECKING:
    from .prim import Prim


class StageVariantSets:
    _prim: Prim

    def __init__(self, prim: Prim) -> None:
        object.__setattr__(self, "_prim", prim)

    def _spec(self) -> PrimSpec:
        return self._prim._edit_spec()

    def __getitem__(self, name: str) -> Any:
        return self._spec().variant_sets[name]

    def __contains__(self, name: str) -> bool:
        return name in self._spec().variant_sets

    def __iter__(self) -> Iterable[str]:
        return iter(self._spec().variant_sets)

    def __len__(self) -> int:
        return len(self._spec().variant_sets)

    def select_variant(self, set_name: str, variant_name: str) -> None:
        variant_set = self._spec().variant_sets[set_name]
        variant_set[variant_name]
        variant_set.select_variant(variant_name)
        self._prim._stage.invalidate()

    def get_variant_selection(self, set_name: str) -> Optional[str]:
        variant_set = self._spec().variant_sets[set_name]
        selected = variant_set.selected_variant
        return selected.name if selected is not None else None
