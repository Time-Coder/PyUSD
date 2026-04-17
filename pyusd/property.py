from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from typeguard import typechecked
from enum import Enum

from .metadata import Metadata

if TYPE_CHECKING:
    from .prim import Prim


class Property:

    class ValueState(Enum):
        Fallback = 0
        NotAuthored = 1
        Authored = 2
        Cleared = 3

    _basic_attrs = {
        "_name",
        "_metadata",
        "_children",
        "_is_leaf",
        "_value_state"
    }

    @typechecked
    def __init__(self, name:str, is_leaf:bool=True)->None:
        self._name:str = name
        self._metadata:Metadata = Metadata()
        self._children:Dict[str, Property] = {}
        self._is_leaf:bool = is_leaf
        self._value_state:Property.ValueState = Property.ValueState.Fallback

    @property
    def is_leaf(self)->bool:
        return self._is_leaf
    
    @property
    def name(self)->str:
        return self._name
    
    @property
    def metadata(self)->Metadata:
        return self._metadata

    def rel(self, prim:Prim)->None:
        from .relationship import Relationship
        self.__class__ = Relationship
        self._targets = [prim]
        self._value_state = Property.ValueState.Authored

    def create(self, attr_type:type)->None:
        from .attribute import Attribute
        self.__class__ = Attribute

    def __getattr__(self, name:str)->Property:
        if name not in self._children:
            self._children[name] = Property(name, is_leaf=False)

        return self._children[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._basic_attrs:
            super().__setattr__(name, value)
            return
        
        from .prim import Prim
        from .attribute import Attribute
        from .relationship import Relationship

        if name in self._children:
            prop = self._children[name]
            if isinstance(prop, Attribute) and isinstance(value, Prim):
                if not prop._custom:
                    raise TypeError(f"cannot assign Prim to Attribute")
                
                del self._children[name]

            if isinstance(prop, Relationship) and not isinstance(value, Prim):
                if not prop._custom:
                    raise TypeError(f"cannot assign none Prim object to Relationship")
                
                del self._children[name]

        if name not in self._children:
            if self._is_leaf:
                raise AttributeError(f"leaf Property cannot create child Property")

            if not isinstance(value, Prim):
                if isinstance(self, Attribute):
                    target_type = self._type
                    target_uniform = self._uniform
                    target_custom = self._custom
                else:
                    target_type = type(value)
                    target_uniform = False
                    target_custom = True

                self._children[name] = Attribute(target_type, self._name + ":" + name, uniform=target_uniform, custom=target_custom, is_leaf=(not target_custom))
            else:
                self._children[name] = Relationship(self._name + ":" + name, is_leaf=False)

        prop = self._children[name]
        if isinstance(prop, Attribute):
            prop.value = value
        elif isinstance(prop, Relationship):
            prop.rel(value)

    def to_str(self, indents:int=0)->str:
        result_list = []
        for child in self._children.values():
            child_str = child.to_str(indents)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result