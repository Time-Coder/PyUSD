from __future__ import annotations
from typing import Dict, TYPE_CHECKING, Optional, KeysView, ValuesView, ItemsView, Iterator

if TYPE_CHECKING:
    from .prim import Prim


class VariantSet:
    
    def __init__(self, name:str, parent_prim:Prim)->None:
        self._name:str = name
        self._parent_prim:Prim = parent_prim
        self._variants:Dict[str, Prim] = {}
        self._selected_variant:Optional[Prim] = None

    @property
    def name(self)->str:
        return self._name

    def select_variant(self, name:str)->Optional[Prim]:
        self._selected_variant = self._variants[name]
        return self._selected_variant

    @property
    def selected_variant(self)->Prim:
        return self._selected_variant

    def __getitem__(self, name:str)->Prim:
        if name not in self._variants:
            from .prim import Prim
            
            variant = Prim(name)
            variant._is_variant = True
            variant._parent = self._parent_prim
            self._variants[name] = variant

        return self._variants[name]
    
    def __delitem__(self, name:str)->None:
        del self._variants[name]

    def keys(self)->KeysView[str]:
        return self._variants.keys()
    
    def values(self)->ValuesView[Prim]:
        return self._variants.values()
    
    def items(self)->ItemsView[str, Prim]:
        return self._variants.items()

    def __iter__(self)->Iterator[str]:
        return iter(self._variants)
    
    def __len__(self)->int:
        return len(self._variants)
    
    def __contains__(self, name:str)->bool:
        return name in self._variants
    
    def to_str(self, indents:int=0)->str:
        tabs = "    " * indents
        result = f'{tabs}variantSet "{self._name}" = {{'

        if self._variants:
            variant_str_list = []
            for variant in self._variants.values():
                variant_str_list.append(variant.to_str(indents + 1))

            result += "\n" + '\n'.join(variant_str_list)

        result += f"{tabs}}}\n"
        
        return result
