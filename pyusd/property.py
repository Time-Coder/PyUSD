from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING, Optional, Union
from typeguard import typechecked
from enum import Enum
import copy

from .metadata import Metadata
from .utils import infer_type, in_annotations

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

    _parent_prim: Optional[Prim]
    _parent_prop: Optional[Property]
    _name: str
    _metadata: Metadata
    _children: Dict[str, Property]
    _is_leaf: bool
    _custom: bool
    _value_state: Property.ValueState

    @typechecked
    def __init__(self, name:str="", doc:str="", metadata:Dict[str, Any]={}, custom:bool=False, is_leaf:bool=True)->None:
        if "doc" in metadata:
            doc = metadata["doc"]

        if doc == "":
            doc = self.__class__.__doc__

        if "doc" not in metadata:
            metadata["doc"] = doc

        self._parent_prim:Optional[Prim] = None
        self._parent_prop:Optional[Property] = None
        self._name:str = name
        self._metadata:Metadata = Metadata(metadata)
        self._children:Dict[str, Property] = {}
        self._custom:bool = custom
        self._is_leaf:bool = is_leaf
        self._value_state:Property.ValueState = Property.ValueState.Fallback

    def clone(self)->Property:
        result = object()
        result.__class__ = self.__class__
        result._parent_prim = None
        result._parent_prop = None
        result._name = self._name
        result._metadata = copy.deepcopy(self._metadata)
        result._children = {}
        result._custom = self._custom
        result._is_leaf = self._is_leaf
        result._value_state = self._value_state
        for name, child in self._children.items():
            result._children[name] = child.clone()
            result._children[name]._parent_prop = result

        return result

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

    @property
    def custom(self)->bool:
        return self._custom

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
        self._value_state = Property.ValueState.NotAuthored
        return self

    def create_prop(self, prop:Property)->Property:
        self._children[prop.name] = prop
        prop._parent_prim = self._parent_prim
        prop._parent_prop = self
        return prop

    def __get__(self, instance:Union[Prim, Property], owner)->Property:
        from .prim import Prim

        if isinstance(instance, Prim):
            return instance._props[self._name]
        elif isinstance(instance, Property):
            return instance._children[self._name]
        
    def __set__(self, instance, prims:Prim):
        from .prim import Prim

        if isinstance(instance, Prim):
            instance._props[self._name].set(prims)
        elif isinstance(instance, Property):
            instance._children[self._name].set(prims)

    def __getattr__(self, name:str)->Property:
        if name not in self._children:
            self.create_prop(Property(name, custom=True, is_leaf=False))

        return self._children[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return
        
        from .prim import Prim
        from .attribute import Attribute
        from .relationship import Relationship

        is_rel:bool = (isinstance(value, Prim) or (isinstance(value, list) and all(isinstance(item, Prim) for item in value)) or isinstance(value, Relationship))
        if name in self._children:
            prop = self._children[name]
            if isinstance(prop, Attribute) and is_rel:
                if not prop._custom:
                    if isinstance(value, Prim):
                        error_message = "cannot assign Prim to Attribute"
                    elif isinstance(value, list):
                        error_message = "cannot assign List[Prim] to Attribute"
                    elif isinstance(value, Relationship):
                        error_message = "cannot assign Relationship to Attribute"

                    raise TypeError(error_message)
                
                del self._children[name]

            if isinstance(prop, Relationship) and not is_rel:
                if not prop._custom:
                    raise TypeError(f"cannot assign {value.__class__} object to Relationship")
                
                del self._children[name]

        if name not in self._children:
            if self._is_leaf:
                raise AttributeError(f"leaf Property cannot create child Property")

        if name not in self._children and isinstance(value, Property):
            if value._parent_prim is None and value._parent_prop is None:
                value._name = name
                self.create_prop(value)
            else:
                cloned_value = value.clone()
                cloned_value._name = name
                self.create_prop(cloned_value)

            return

        if name not in self._children:
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

                self.create_prop(Attribute(target_type, name, uniform=target_uniform, custom=target_custom, is_leaf=(not target_custom), fix_type=target_fix_type))
            else:
                self.create_prop(Relationship(name, custom=target_custom, is_leaf=False))

        self._children[name].set(value)

    def to_str(self, indents:int=0)->str:
        result_list = []
        for child in self._children.values():
            child_str = child.to_str(indents)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result