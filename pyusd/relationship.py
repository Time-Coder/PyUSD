from __future__ import annotations
from typing import List, TYPE_CHECKING, Dict, Any
from typeguard import typechecked

from .property import Property
from .utils import usd_value_str

if TYPE_CHECKING:
    from .prim import Prim


class Relationship(Property):

    _targets: List[Prim]

    @typechecked
    def __init__(self, name:str, metadata:Dict[str, Any]={}, custom:bool=False, is_leaf:bool=True)->None:
        Property.__init__(self, name, metadata=metadata, custom=custom, is_leaf=is_leaf)
        self._targets:List[Prim] = []

    @property
    def targets(self)->List[Prim]:
        return self._targets
    
    def rel(self, prim:Prim)->None:
        self._targets.append(prim)
        self._value_state = Property.ValueState.Authored

    def add_target(self, prim:Prim)->None:
        self._targets.append(prim)
        self._value_state = Property.ValueState.Authored

    def remove_target(self, prim:Prim)->None:
        self._targets.remove(prim)
        self._value_state = Property.ValueState.Authored

    def __str__(self)->str:
        if len(self._targets) == 0:
            return ""
        elif len(self._targets) == 1:
            return str(self._targets[0])
        else:
            return str(self._targets)
    
    def to_str(self, indents:int=0)->str:
        result_list = []
        if self._value_state != Property.ValueState.Fallback:
            tabs = "    " * indents
            prefix = ""
            if self._custom:
                prefix += "custom "

            line = f"{tabs}{prefix}rel {self.full_name}"
            if self._value_state != Property.ValueState.NotAuthored:
                line += f" = {usd_value_str(self._targets, indents, True)}"

            metadata_str = self._metadata.to_str(indents)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

        for child in self._children.values():
            child_str = child.to_str(indents)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result
    