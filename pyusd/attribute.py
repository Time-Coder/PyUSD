from __future__ import annotations
from typing import Dict, Any, TypeVar, Generic, Optional
from collections.abc import Iterable
from typeguard import typechecked
import copy

from .property import Property
from .dtypes import namespace
from .utils import nest_map, usd_type_str, usd_value_str, analyze_list_type, infer_type, usd_scalar_types, usd_vector_types, usd_quat_types, usd_matrix_types


T = TypeVar('T')
class Attribute(Property, Generic[T]):

    _type: type
    _dtype: type
    _array_dim: int
    _time_samples: Dict[float, T]
    _value: Optional[T]
    _uniform: bool
    _fix_type: bool

    @typechecked
    def __init__(self, value_type:type, name:str="", value:Optional[T]=None, doc:str="", metadata:Dict[str, Any]={}, is_leaf:bool=True, uniform:bool=False, custom:bool=False, fix_type:bool=True)->None:
        Property.__init__(self, name, doc=doc, metadata=metadata, custom=custom, is_leaf=is_leaf)
        self._init(value_type, value, uniform, fix_type)
    
    def _init(self, value_type:type, value:Optional[T]=None, uniform:bool=False, fix_type:bool=True)->None:
        dtype, array_dim = analyze_list_type(value_type)
        self._type:type = value_type
        self._dtype:type = dtype
        self._array_dim:int = array_dim
        self._value:Optional[T] = self._convert_from(value)
        self._time_samples:Dict[float, T] = {}
        self._uniform:bool = uniform
        self._fix_type:bool = fix_type

    def clone(self)->Attribute[T]:
        result = Property.clone(self)
        result._type = self._type
        result._dtype = self._dtype
        result._array_dim = self._array_dim
        result._value = self._convert_from(self._value)
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

    def get(self)->T:
        return self.value

    def set(self, value:Any)->None:
        self.value = value

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

    @property
    def is_namespace(self)->bool:
        return (self._type == namespace)
    
    @property
    def type(self)->type:
        return self._type

    @property
    def type_name(self)->str:
        return usd_type_str(self._dtype, self._array_dim)

    @typechecked
    def value_str(self, indent:int=0)->str:
        return usd_value_str(self.value, indent)

    def to_str(self, indents:int=0)->str:
        result_list = []
        full_name = self.full_name
        if self.value_state != Property.ValueState.Fallback:
            tabs = "    " * indents
            prefix = ""
            if self._custom:
                prefix += "custom "
            if self._uniform:
                prefix += "uniform "

            line = f"{tabs}{prefix}{self.type_name} {full_name}"
            if self.value_state != Property.ValueState.NotAuthored:
                line += f" = {self.value_str(indents)}"

            metadata_str = self._metadata.to_str(indents)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

            if self._time_samples:
                line = f"{tabs}{prefix}{self.type_name} {full_name}.timeSamples = " + usd_value_str(self._time_samples, indents)
                result_list.append(line)

        for child in self._children.values():
            child_str = child.to_str(indents)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result

    def _convert_from(self, value:Any)->T:
        if isinstance(value, Attribute):
            value = value.value

        if value is None:
            return value

        current_type = infer_type(value)
        if current_type == self._type:
            return value
        
        current_dtype, current_array_dim = analyze_list_type(current_type)
        if self._array_dim == current_array_dim and self._dtype == current_dtype:
            return value
        
        if not self._fix_type:
            self._dtype, self._array_dim = current_dtype, current_array_dim
            self._type = current_type
            return value

        if self._array_dim != current_array_dim:
            raise TypeError(f"cannot convert {current_type} to {self._type}")

        if self._dtype in usd_scalar_types:
            return nest_map(value, self._dtype)
        elif self._dtype in usd_vector_types or self._dtype in usd_quat_types:
            if issubclass(current_dtype, Iterable):
                return nest_map(value, lambda x: self._dtype(*x))
            else:
                return nest_map(value, self._dtype)
        elif self._dtype in usd_matrix_types:
            if issubclass(current_dtype, Iterable):
                
                def func(x):
                    args = []
                    subvec_type = self._dtype.subvec_type()
                    for sub_value in x:
                        if isinstance(sub_value, subvec_type):
                            args.append(sub_value)
                        elif isinstance(sub_value, Iterable):
                            args.append(subvec_type(*sub_value))
                        else:
                            args.append(subvec_type(sub_value))
                    return self._type(*args)
                
                return nest_map(value, func)
            else:
                return nest_map(value, self._dtype)
        else:
            raise TypeError(f"canot convert {current_type} to {self._type}")

    @staticmethod
    def _other_value(other:Any)->T:
        if isinstance(other, Attribute):
            return other.value

        return other

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
        if "_children" not in self.__dict__ or "_value" not in self.__dict__:
            return Property.__setattr__(self, name, value)

        if name in self._children:
            return Property.__setattr__(self, name, value)
        elif hasattr(self._value, name):
            return setattr(self._value, name, value)
        else:
            return Property.__setattr__(self, name, value)

    def __str__(self)->str:
        return str(self.value)
    
    def __repr__(self)->str:
        return repr(self.value)

    def __add__(self, other:Any)->Any:
        return self.value + self._other_value(other)
    
    def __radd__(self, other:Any)->Any:
        return self._other_value(other) + self.value
    
    def __iadd__(self, other:Any)->Any:
        self.value += self._other_value(other)
        return self

    def __sub__(self, other:Any)->Any:
        return self.value - self._other_value(other)
    
    def __rsub__(self, other:Any)->Any:
        return self._other_value(other) - self.value
    
    def __isub__(self, other:Any)->Any:
        self.value -= self._other_value(other)
        return self

    def __mul__(self, other:Any)->Any:
        return self.value * self._other_value(other)
    
    def __rmul__(self, other:Any)->Any:
        return self._other_value(other) * self.value
    
    def __imul__(self, other:Any)->Any:
        self.value *= self._other_value(other)
        return self

    def __truediv__(self, other:Any)->Any:
        return self.value / self._other_value(other)
    
    def __rtruediv__(self, other:Any)->Any:
        return self._other_value(other) / self.value
    
    def __itruediv__(self, other:Any)->Any:
        self.value /= self._other_value(other)
        return self

    def __floordiv__(self, other:Any)->Any:
        return self.value // self._other_value(other)
    
    def __rfloordiv__(self, other:Any)->Any:
        return self._other_value(other) // self.value
    
    def __ifloordiv__(self, other:Any)->Any:
        self.value //= self._other_value(other)
        return self

    def __mod__(self, other:Any)->Any:
        return self.value % self._other_value(other)
    
    def __rmod__(self, other:Any)->Any:
        return self._other_value(other) % self.value
    
    def __imod__(self, other:Any)->Any:
        self.value %= self._other_value(other)
        return self

    def __pow__(self, other:Any)->Any:
        return self.value ** self._other_value(other)
    
    def __rpow__(self, other:Any)->Any:
        return self._other_value(other) ** self.value
    
    def __ipow__(self, other:Any)->Any:
        self.value **= self._other_value(other)
        return self

    def __eq__(self, other:Any)->bool:        
        return (self.value == self._other_value(other))
    
    def __req__(self, other:Any)->bool:
        return (self._other_value(other) == self.value)
    
    def __ne__(self, other:Any)->bool:        
        return (self.value != self._other_value(other))
    
    def __rne__(self, other:Any)->bool:
        return (self._other_value(other) != self.value)
    
    def __gt__(self, other:Any)->bool:        
        return (self.value > self._other_value(other))
    
    def __rgt__(self, other:Any)->bool:
        return (self._other_value(other) > self.value)
    
    def __lt__(self, other:Any)->bool:        
        return (self.value < self._other_value(other))
    
    def __rlt__(self, other:Any)->bool:
        return (self._other_value(other) < self.value)
    
    def __ge__(self, other:Any)->bool:        
        return (self.value >= self._other_value(other))
    
    def __rge__(self, other:Any)->bool:
        return (self._other_value(other) >= self.value)
    
    def __le__(self, other:Any)->bool:        
        return (self.value <= self._other_value(other))
    
    def __rle__(self, other:Any)->bool:
        return (self._other_value(other) <= self.value)

    def __contains__(self, item:Any)->bool:
        return (self._other_value(item) in self.value)
    
    def __len__(self)->int:
        return len(self.value)
    
    def __getitem__(self, name:Any)->Any:
        return self.value[self._other_value(name)]
    
    def __setitem__(self, name:Any, value:Any)->None:
        self.value[self._other_value(name)] = self._other_value(value)