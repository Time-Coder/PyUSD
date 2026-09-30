from __future__ import annotations

from typing import TYPE_CHECKING, Dict, ItemsView, Iterator, KeysView, ValuesView

from .variant_set import VariantSet

if TYPE_CHECKING:
    from .prim_spec import PrimSpec


class VariantSets:

    def __init__(self, parent_prim:PrimSpec)->None:
        self._parent_prim:PrimSpec = parent_prim
        self._variant_sets:Dict[str, VariantSet] = {}

    def __getitem__(self, name:str)->VariantSet:
        if name not in self._variant_sets:
            self._variant_sets[name] = VariantSet(name, self._parent_prim)

        return self._variant_sets[name]

    def __delitem__(self, name:str)->None:
        del self._variant_sets[name]

    def keys(self)->KeysView[str]:
        return self._variant_sets.keys()

    def values(self)->ValuesView[VariantSet]:
        return self._variant_sets.values()

    def items(self)->ItemsView[str, VariantSet]:
        return self._variant_sets.items()

    def __iter__(self)->Iterator[str]:
        return iter(self._variant_sets)

    def __len__(self)->int:
        return len(self._variant_sets)

    def __contains__(self, name:str)->bool:
        return name in self._variant_sets
