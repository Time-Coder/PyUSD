from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING, Optional
from typeguard import typechecked
from enum import Enum

from .metadata import Metadata
from .utils import infer_type

if TYPE_CHECKING:
    from .prim import Prim
    from .attribute import Attribute
    from .relationship import Relationship


class Property:

    class ValueState(Enum):
        Fallback = 0
        NotAuthored = 1
        Authored = 2
        Cleared = 3

    _basic_attrs = {
        "_parent_prim",
        "_parent_prop",
        "_name",
        "_metadata",
        "_children",
        "_is_leaf",
        "_value_state"
    }

    @typechecked
    def __init__(self, name:str, is_leaf:bool=True)->None:
        self._parent_prim:Optional[Prim] = None
        self._parent_prop:Optional[Property] = None
        self._name:str = name
        self._metadata:Metadata = Metadata()
        self._children:Dict[str, Property] = {}
        self._is_leaf:bool = is_leaf
        self._value_state:Property.ValueState = Property.ValueState.Fallback

    @property
    def parent_prim(self)->Prim:
        return self._parent_prim
    
    @property
    def parent_prop(self)->Property:
        return self._parent_prop

    @property
    def is_leaf(self)->bool:
        return self._is_leaf
    
    @property
    def name(self)->str:
        return self._name
    
    @property
    def full_name(self)->str:
        if self._parent_prop is None:
            return self._name
        
        return self._parent_prop.full_name + ":" + self._name
    
    @property
    def path(self)->str:
        if self._parent_prim is None:
            return self.full_name
        
        return self._parent_prim.path + "." + self.full_name
    
    @property
    def metadata(self)->Metadata:
        return self._metadata
    
    @property
    def value_state(self)->Property.ValueState:
        return self._value_state

    def rel(self, prim:Prim)->Relationship:
        if self.__class__.__name__ != "Property":
            raise AttributeError(f"'{self.__class__.__name__}' object has not attribute 'rel'")

        from .relationship import Relationship
        self.__class__ = Relationship
        self._targets = [prim]
        self._value_state = Property.ValueState.Authored
        return self

    def create(self, value_type:type, value:Optional[Any]=None, uniform:bool=False, custom:bool=False, fix_type:bool=True)->Attribute:
        if self.__class__.__name__ != "Property":
            raise AttributeError(f"'{self.__class__.__name__}' object has not attribute 'create'")
        
        from .attribute import Attribute
        self.__class__ = Attribute
        Attribute._init(self, value_type, value, uniform, custom, fix_type)
        return self

    def _add_prop(self, prop:Property)->None:
        self._children[prop.name] = prop
        prop._parent_prim = self._parent_prim
        prop._parent_prop = self

    def __getattr__(self, name:str)->Property:
        if name not in self._children:
            self._add_prop(Property(name, is_leaf=False))

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
                    target_fix_type = self._fix_type
                else:
                    target_type = infer_type(value)
                    target_uniform = False
                    target_custom = True
                    target_fix_type = False

                self._add_prop(Attribute(target_type, name, uniform=target_uniform, custom=target_custom, is_leaf=(not target_custom), fix_type=target_fix_type))
            else:
                self._add_prop(Relationship(name, is_leaf=False))

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