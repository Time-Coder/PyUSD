from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict,
    ItemsView,
    Iterator,
    KeysView,
    Optional,
    ValuesView,
)

from .variant_set_serializer import VariantSetSerializer

if TYPE_CHECKING:
    from .prim import PrimSpec


class VariantSet:

    def __init__(self, name:str, parent_prim:PrimSpec)->None:
        self._name:str = name
        self._parent_prim:PrimSpec = parent_prim
        self._variants:Dict[str, PrimSpec] = {}
        self._selected_variant:Optional[PrimSpec] = None

    @property
    def name(self)->str:
        return self._name

    def select_variant(self, name:str)->Optional[PrimSpec]:
        self._selected_variant = self._variants[name]
        self._parent_prim._touch()
        return self._selected_variant

    @property
    def selected_variant(self)->PrimSpec:
        return self._selected_variant

    def __getitem__(self, name:str)->PrimSpec:
        if name not in self._variants:
            from .prim import PrimSpec

            variant = PrimSpec(name)
            variant._is_variant = True
            variant._parent = self._parent_prim
            self._variants[name] = variant
            self._parent_prim._touch()

        return self._variants[name]

    def __delitem__(self, name:str)->None:
        del self._variants[name]

    def keys(self)->KeysView[str]:
        return self._variants.keys()

    def values(self)->ValuesView[PrimSpec]:
        return self._variants.values()

    def items(self)->ItemsView[str, PrimSpec]:
        return self._variants.items()

    def __iter__(self)->Iterator[str]:
        return iter(self._variants)

    def __len__(self)->int:
        return len(self._variants)

    def __contains__(self, name:str)->bool:
        return name in self._variants

    def to_str(self, indents:int=0)->str:
        return VariantSetSerializer.to_str(self, indents)
