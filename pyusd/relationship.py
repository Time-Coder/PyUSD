from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .property import Property
from .relationship_serializer import RelationshipSerializer

if TYPE_CHECKING:
    from .prim import PrimSpec


class Relationship(Property):

    _targets: List[PrimSpec]

    def __init__(self, name:str="", doc:str="", metadata:Optional[Dict[str, Any]]=None, custom:bool=False, is_leaf:bool=True)->None:
        Property.__init__(self, name, doc=doc, metadata=metadata, custom=custom, is_leaf=is_leaf)
        self._targets:List[PrimSpec] = []

    @property
    def value_state(self)->Property.ValueState:
        if self._value_state != Property.ValueState.Authored and self._targets:
            return Property.ValueState.Authored

        return self._value_state

    def clone(self, clone_children:bool=True)->Relationship:
        result = Property.clone(self, clone_children)
        result._targets = copy.copy(self._targets)
        return result

    def set(self, prims:Union[List[PrimSpec], PrimSpec, Relationship])->None:
        if isinstance(prims, list):
            self._targets = prims
        elif isinstance(prims, Relationship):
            self._targets = copy.copy(prims._targets)
        else:
            self._targets = [prims]
        self._value_state = Property.ValueState.Authored
        self._touch()

    def get(self)->List[PrimSpec]:
        return self._targets

    @property
    def targets(self)->List[PrimSpec]:
        return self._targets

    def rel(self, prim:PrimSpec)->None:
        self._targets.append(prim)
        self._value_state = Property.ValueState.Authored
        self._touch()

    def add_target(self, prim:PrimSpec)->None:
        self._targets.append(prim)
        self._value_state = Property.ValueState.Authored
        self._touch()

    def remove_target(self, prim:PrimSpec)->None:
        self._targets.remove(prim)
        self._value_state = Property.ValueState.Authored
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
