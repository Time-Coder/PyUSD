from __future__ import annotations

from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from typing import TYPE_CHECKING, Dict

from .variant_set_spec import VariantSetSpec

if TYPE_CHECKING:
    from .prim_spec import PrimSpec


class VariantSetsSpec:

    def __init__(self, parent_prim:PrimSpec)->None:
        self._parent_prim:PrimSpec = parent_prim
        self._variant_sets:Dict[str, VariantSetSpec] = {}

    def __getitem__(self, name:str)->VariantSetSpec:
        if name not in self._variant_sets:
            self._variant_sets[name] = VariantSetSpec(name, self._parent_prim)

        return self._variant_sets[name]

    def variant_set(self, name:str)->VariantSetSpec:
        """This layer's variant set called ``name``.

        Raises ``KeyError`` when this layer does not declare it. That is why the
        composed :class:`~pyusd.variant_sets.VariantSets` tests membership itself
        rather than delegating the question: it walks every contributing layer
        asking whether one declares a set, and a layer that does not is the
        ordinary case rather than an error. Membership is the way to ask, because
        :meth:`__getitem__` would declare the set it is trying to find out about.
        """
        return self._variant_sets[name]

    def __delitem__(self, name:str)->None:
        del self._variant_sets[name]

    def keys(self)->KeysView[str]:
        return self._variant_sets.keys()

    def values(self)->ValuesView[VariantSetSpec]:
        return self._variant_sets.values()

    def items(self)->ItemsView[str, VariantSetSpec]:
        return self._variant_sets.items()

    def __iter__(self)->Iterator[str]:
        return iter(self._variant_sets)

    def __len__(self)->int:
        return len(self._variant_sets)

    def __contains__(self, name:str)->bool:
        return name in self._variant_sets
