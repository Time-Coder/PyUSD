from __future__ import annotations
from typing import Dict, Any, TypeVar, Generic, Optional
from collections.abc import Iterable
from typeguard import typechecked

from .property import Property
from .dtypes import namespace
from .utils import usd_type_str, usd_value_str, analyze_list_type


T = TypeVar('T')
class Attribute(Property, Generic[T]):

    _basic_attrs = Property._basic_attrs | {
        "_type",
        "_dtype",
        "_array_dim",
        "_time_samples",
        "_value",
        "_uniform",
        "_children",
        "value",
        "uniform",
        "_custom",
    }

    @typechecked
    def __init__(self, value_type:type, name:str, is_leaf:bool=True, uniform:bool=False, custom:bool=False)->None:
        Property.__init__(self, name, is_leaf)
        dtype, array_dim = analyze_list_type(value_type)

        self._type:type = value_type
        self._dtype:type = dtype
        self._array_dim:int = array_dim
        self._time_samples:Dict[float, T] = {}
        self._value:Optional[T] = None
        self._uniform:bool = uniform
        self._custom:bool = custom
    
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
    def uniform(self)->bool:
        return self._uniform

    @uniform.setter
    @typechecked
    def uniform(self, flag:bool)->None:
        self._uniform = flag

    @property
    def custom(self)->bool:
        return self._custom

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
        if self._value_state != Property.ValueState.Fallback:
            tabs = "    " * indents
            prefix = ""
            if self._custom:
                prefix += "custom "
            if self._uniform:
                prefix += "uniform "

            line = f"{tabs}{prefix}{self.type_name} {self._name}"
            if self._value_state != Property.ValueState.NotAuthored:
                line += f" = {self.value_str(indents)}"

            metadata_str = self._metadata.to_str(indents)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

            if self._time_samples:
                line = f"{tabs}{prefix}{self.type_name} {self._name}.timeSamples = " + usd_value_str(self._time_samples, indents)
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

        current_type = type(value)
        if current_type == self._type:
            return value

        if self._type in Attribute.__scalar_types:
            return self._type(value)
        elif self._type in Attribute.__vector_types or self._type in Attribute.__quat_types:
            if isinstance(value, Iterable):
                return self._type(*value)
            else:
                return self._type(value)
        elif self._type in Attribute.__matrix_types:
            if isinstance(value, Iterable):
                args = []
                subvec_type = self._type.subvec_type()
                for sub_value in value:
                    if isinstance(sub_value, subvec_type):
                        args.append(sub_value)
                    elif isinstance(sub_value, Iterable):
                        args.append(subvec_type(*sub_value))
                    else:
                        args.append(subvec_type(sub_value))
                return self._type(*args)
            else:
                return self._type(value)
        else:
            raise TypeError(f"canot convert {type(value)} to {self._type}")

    @staticmethod
    def _other_value(other:Any)->T:
        if isinstance(other, Attribute):
            return other.value

        return other

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

    