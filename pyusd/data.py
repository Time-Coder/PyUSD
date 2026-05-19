from typing import Any, TypeVar, Optional, Iterable, Generic

from typeguard import typechecked

from .utils import in_annotations, analyze_list_type, usd_scalar_types, usd_vector_types, usd_quat_types, usd_matrix_types, infer_type, nest_map, usd_type_str, usd_value_str
from .dtypes import token, namespace


T = TypeVar('T')
class Data(Generic[T]):

    _type: type
    _dtype: type
    _array_dim: int
    _value: Optional[T]

    def __init__(self, value_type: type, value: Optional[T])->None:
        dtype, array_dim = analyze_list_type(value_type)
        self._type:type = value_type
        self._dtype:type = dtype
        self._array_dim:int = array_dim
        self._value:Optional[T] = self._convert_from(value)

    @property
    def value(self)->Optional[T]:
        return self._value
    
    @value.setter
    def value(self, value:Optional[T])->None:
        self._value = value

    @property
    def type(self)->type:
        return self._type
    
    @property
    def type_name(self)->str:
        return usd_type_str(self._dtype, self._array_dim)
    
    @property
    def is_namespace(self)->bool:
        return (self._type == namespace)

    @typechecked
    def value_str(self, indent:int=0)->str:
        return usd_value_str(self.value, indent)

    def get(self)->T:
        return self.value

    def set(self, value:Optional[T])->None:
        self.value = value

    def __getattr__(self, name:str)->Any:
        if hasattr(self._value, name):
            return getattr(self._value, name)
        else:
            return super().__getattr__(name)
        
    def __setattr__(self, name:str, value:Any)->None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return
        
        if hasattr(self._value, name):
            return setattr(self._value, name, value)
        else:
            return super().__setattr__(name, value)

    def _convert_from(self, value:Any)->T:
        if value is None:
            return value
        
        current_type = infer_type(value)
        
        if isinstance(value, Data):
            value = value.value

        if value is None:
            return value
        
        if current_type == self._type or current_type == str and self._type == token:
            return value
        
        current_dtype, current_array_dim = analyze_list_type(current_type)
        if self._array_dim == current_array_dim and self._dtype == current_dtype:
            return value

        if self._array_dim != current_array_dim:
            raise TypeError(f"cannot convert {current_type} to {self._type}")

        if issubclass(self._dtype, usd_scalar_types):
            return nest_map(value, self._dtype)
        elif issubclass(self._dtype, usd_vector_types + usd_quat_types):
            if issubclass(current_dtype, Iterable):
                return nest_map(value, lambda x: self._dtype(*x))
            else:
                return nest_map(value, self._dtype)
        elif issubclass(self._dtype, usd_matrix_types):
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
        if isinstance(other, Data):
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

    def __contains__(self, item:Any)->bool:
        return (self._other_value(item) in self.value)
    
    def __len__(self)->int:
        return len(self.value)
    
    def __getitem__(self, name:Any)->Any:
        return self.value[self._other_value(name)]
    
    def __setitem__(self, name:Any, value:Any)->None:
        self.value[self._other_value(name)] = self._other_value(value)