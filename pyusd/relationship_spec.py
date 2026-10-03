from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from .property_spec import PropertySpec
from .relationship_serializer import RelationshipSerializer

if TYPE_CHECKING:
    from .prim_spec import PrimSpec


class RelationshipSpec(PropertySpec):

    _targets: List[PrimSpec]

    def __init__(self, name:str="", doc:str="", metadata:Optional[Dict[str, Any]]=None, custom:bool=False, is_leaf:bool=True)->None:
        PropertySpec.__init__(self, name, doc=doc, metadata=metadata, custom=custom, is_leaf=is_leaf)
        self._targets:List[PrimSpec] = []

    @property
    def value_state(self)->PropertySpec.ValueState:
        if self._value_state != PropertySpec.ValueState.Authored and self._targets:
            return PropertySpec.ValueState.Authored

        return self._value_state

    def clone(self, clone_child:bool=True)->RelationshipSpec:
        result = PropertySpec.clone(self, clone_child)
        result._targets = copy.copy(self._targets)
        return cast(RelationshipSpec, result)

    def set(self, prims:Union[List[PrimSpec], PrimSpec, RelationshipSpec])->None:
        if isinstance(prims, list):
            self._targets = prims
        elif isinstance(prims, RelationshipSpec):
            self._targets = copy.copy(prims._targets)
        else:
            self._targets = [prims]
        self._value_state = PropertySpec.ValueState.Authored
        self._touch()

    def get(self)->List[PrimSpec]:
        return self._targets

    @property
    def targets(self)->List[PrimSpec]:
        return self._targets

    def rel(self, prim:PrimSpec)->RelationshipSpec:
        self._targets.append(prim)
        self._value_state = PropertySpec.ValueState.Authored
        self._touch()
        return self

    def add_target(self, prim:PrimSpec)->None:
        self._targets.append(prim)
        self._value_state = PropertySpec.ValueState.Authored
        self._touch()

    def remove_target(self, prim:PrimSpec)->None:
        self._targets.remove(prim)
        self._value_state = PropertySpec.ValueState.Authored
        self._touch()

    def __str__(self)->str:
        if len(self._targets) == 0:
            return ""
        elif len(self._targets) == 1:
            return str(self._targets[0])
        else:
            return str(self._targets)

    def to_str(self, indents:int=0, full:bool=False)->str:
        return RelationshipSerializer.to_str(self, indents, full)
