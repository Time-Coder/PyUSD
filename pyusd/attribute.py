from __future__ import annotations
from typing import Dict, Any, TypeVar, Optional
from typeguard import typechecked
import copy

from .data import Data
from .property import Property
from .dtypes import namespace, token
from .utils import usd_value_str, in_annotations


T = TypeVar('T')
class Attribute(Property, Data[T]):

    _time_samples: Dict[float, T]
    _uniform: bool
    _fix_type: bool

    @typechecked
    def __init__(self, value_type:type, name:str="", value:Optional[T]=None, doc:str="", metadata:Optional[Dict[str, Any]]=None, is_leaf:bool=True, uniform:bool=False, custom:bool=False, fix_type:bool=True)->None:
        if metadata is None:
            metadata = {}
        
        if isinstance(value_type, type) and issubclass(value_type, token) and value_type != token:
            metadata["allowedTokens"] = [member.value for member in value_type]

        Property.__init__(self, name, doc=doc, metadata=metadata, custom=custom, is_leaf=is_leaf)
        self._init(value_type, value, uniform, fix_type)
    
    def _init(self, value_type:type, value:Optional[T]=None, uniform:bool=False, fix_type:bool=True)->None:
        Data.__init__(self, value_type, value)
        self._time_samples:Dict[float, T] = {}
        self._uniform:bool = uniform
        self._fix_type:bool = fix_type

    def clone(self, clone_children:bool=True)->Attribute[T]:
        result = Property.clone(self, clone_children)
        result._type = self._type
        result._dtype = self._dtype
        result._array_dim = self._array_dim
        result._value = copy.deepcopy(self._value)
        result._time_samples = copy.deepcopy(self._time_samples)
        result._uniform = self._uniform
        result._fix_type = self._fix_type
        return result

    @property
    def timeSamples(self)->Dict[float, T]:
        return self._time_samples
    
    @property
    def value(self)->T:
        return self._value
    
    @value.setter
    def value(self, value:T)->None:
        if value is self:
            return

        self._value = self._convert_from(value)
        self._value_state = Attribute.ValueState.Authored

    def clear(self)->None:
        self._value = None
        self._value_state = Attribute.ValueState.Cleared

    @property
    def value_state(self)->Attribute.ValueState:
        if self._value_state != Attribute.ValueState.Authored and isinstance(self._value, list) and self._value:
            return Attribute.ValueState.Authored

        return self._value_state

    @property
    def uniform(self)->bool:
        return self._uniform

    @uniform.setter
    @typechecked
    def uniform(self, flag:bool)->None:
        self._uniform = flag

    def to_str(self, indents:int=0, full:bool=False)->str:
        result_list = []
        full_name = self.full_name
        if (full or self.value_state != Property.ValueState.Fallback) and self._type != namespace:
            tabs = "    " * indents
            prefix = ""
            if self._custom:
                prefix += "custom "
            if self._uniform:
                prefix += "uniform "

            line = f"{tabs}{prefix}{self.type_name} {full_name}"
            if (
                (self.value_state == Property.ValueState.Fallback and self._value is not None) or
                self.value_state in [Property.ValueState.Authored, Property.ValueState.Cleared]
            ):
                line += f" = {self.value_str(indents)}"

            metadata_str = self._metadata.to_str(indents, full=full)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

            if self._time_samples:
                line = f"{tabs}{prefix}{self.type_name} {full_name}.timeSamples = " + usd_value_str(self._time_samples, indents)
                result_list.append(line)

        for child in self._children.values():
            child_str = child.to_str(indents, full=full)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result

    def __getattr__(self, name:str)->Any:
        if "_children" not in self.__dict__ or "_value" not in self.__dict__:
            return Property.__getattr__(self, name)

        if name in self._children:
            return self._children[name]
        elif hasattr(self._value, name):
            return getattr(self._value, name)
        else:
            return Property.__getattr__(self, name)
        
    def __setattr__(self, name:str, value:Any)->None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return
        
        if "_children" not in self.__dict__ or "_value" not in self.__dict__:
            return Property.__setattr__(self, name, value)

        if name in self._children:
            return Property.__setattr__(self, name, value)
        elif hasattr(self._value, name):
            return setattr(self._value, name, value)
        else:
            return Property.__setattr__(self, name, value)
