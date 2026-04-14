from __future__ import annotations
from typing import Dict, Any, Optional
from collections.abc import Iterable
from typeguard import typechecked

from .gf import double2, double3, double4, float2, float3, float4, int2, int3, int4, matrix2d, matrix3d, matrix4d, quatf, quatd, genType


class NoOpinonType:
    
    def __str__(self)->str:
        return "NoOpinion"

NoOpinion = NoOpinonType()

class Attribute:

    __type_map = {
        "bool": bool,
        "double": float,
        "float": float,
        "half": float,
        "int": int,
        "int64": int,
        "string": str,
        "token": str,
        "timecode": float,
        "uchar": int,
        "uint": int,
        "uint64": int,
        "double2": double2,
        "double3": double3,
        "double4": double4,
        "float2": float2,
        "float3": float3,
        "float4": float4,
        "int2": int2,
        "int3": int3,
        "int4": int4,
        "matrix2d": matrix2d,
        "matrix3d": matrix3d,
        "matrix4d": matrix4d,
        "quatf": quatf,
        "quatd": quatd
    }

    __scalar_types = [
        "bool",
        "double",
        "float",
        "half",
        "int",
        "int64",
        "string",
        "token",
        "timecode",
        "uchar",
        "uint",
        "uint64"
    ]

    __vector_types = [
        "double2",
        "double3",
        "double4",
        "float2",
        "float3",
        "float4",
        "int2",
        "int3",
        "int4"
    ]

    __matrix_types = [
        "matrix2d",
        "matrix3d",
        "matrix4d"
    ]

    __quat_types = [
        "quatf",
        "quatd"
    ]

    __basic_attrs = [
        "_target_type",
        "_type_name",
        "_name",
        "_time_samples",
        "_value",
        "_extentable",
        "_uniform",
        "_children",
        "value",
        "uniform",

    ]

    def __init__(self, type_name:str, name:str, extentable:bool=False)->None:
        if type_name in Attribute.__type_map:
            self._target_type:Optional[type] = Attribute.__type_map[type_name]
        else:
            self._target_type:Optional[type] = None

        self._type_name:str = type_name
        self._name:str = name
        self._time_samples:Dict[float, Any] = {}
        self._value:Any = NoOpinion
        self._extentable:bool = extentable
        self._uniform:bool = False
        self._children:Dict[str, Attribute] = {}

    @property
    def type_name(self)->str:
        return self._type_name
    
    @property
    def name(self)->str:
        return self._name
    
    @property
    def time_samples(self)->Dict[float, Any]:
        return self._time_samples
    
    @property
    def value(self)->Any:
        return self._value
    
    @value.setter
    def value(self, value:Any)->None:
        self._value = self._convert_from(value)

    @property
    def uniform(self)->bool:
        return self._uniform

    @uniform.setter
    @typechecked
    def uniform(self, flag:bool)->None:
        self._uniform = flag

    @property
    def is_namespace(self)->bool:
        return (self._type_name == "namespace")

    @property
    def is_extentable(self)->bool:
        return self._extentable

    @property
    def usd_str(self)->str:
        if isinstance(self.value, genType):
            return self.value.usd_str
        else:
            return str(self.value)

    def to_str(self, indents:int=0)->str:
        result_list = []
        if self._value is not NoOpinion:
            tabs = "    " * indents
            if self._uniform:
                result_list.append(f"{tabs}uniform {self._type_name} {self._name} = {self.usd_str}")
            else:
                result_list.append(f"{tabs}{self._type_name} {self._name} = {self.usd_str}")

        for child in self._children.values():
            child_str = child.to_str(indents)
            if child_str:
                result_list.append(child_str)

        return "\n".join(result_list)

    def _convert_from(self, value:Any)->Any:
        if value is NoOpinion or value is None:
            return value

        current_type = type(value)
        if current_type == self._target_type:
            return value

        if self._type_name in Attribute.__scalar_types:
            return self._target_type(value)
        elif self._type_name in Attribute.__vector_types or self._type_name in Attribute.__quat_types:
            if isinstance(value, Iterable):
                return self._target_type(*value)
            else:
                return self._target_type(value)
        elif self._type_name in Attribute.__matrix_types:
            if isinstance(value, Iterable):
                args = []
                subvec_type = self._target_type.subvec_type()
                for sub_value in value:
                    if isinstance(sub_value, subvec_type):
                        args.append(sub_value)
                    elif isinstance(sub_value, Iterable):
                        args.append(subvec_type(*sub_value))
                    else:
                        args.append(subvec_type(sub_value))
                return self._target_type(*args)
            else:
                return self._target_type(value)

    @staticmethod
    def _other_value(other:Any)->Any:
        if isinstance(other, Attribute):
            return other.value

        return other

    def __str__(self)->str:
        return str(self.value)

    def __add__(self, other:Any)->Any:
        return self.value + self._other_value(other)
    
    def __radd__(self, other:Any)->Any:
        return self._other_value(other) + self.value
    
    def __iadd__(self, other:Any)->Any:
        self.value += self._other_value(other)
        return self.value

    def __sub__(self, other:Any)->Any:
        return self.value - self._other_value(other)
    
    def __rsub__(self, other:Any)->Any:
        return self._other_value(other) - self.value
    
    def __isub__(self, other:Any)->Any:
        self.value -= self._other_value(other)
        return self.value

    def __mul__(self, other:Any)->Any:
        return self.value * self._other_value(other)
    
    def __rmul__(self, other:Any)->Any:
        return self._other_value(other) * self.value
    
    def __imul__(self, other:Any)->Any:
        self.value *= self._other_value(other)
        return self.value

    def __truediv__(self, other:Any)->Any:
        return self.value / self._other_value(other)
    
    def __rtruediv__(self, other:Any)->Any:
        return self._other_value(other) / self.value
    
    def __itruediv__(self, other:Any)->Any:
        self.value /= self._other_value(other)
        return self.value

    def __floordiv__(self, other:Any)->Any:
        return self.value // self._other_value(other)
    
    def __rfloordiv__(self, other:Any)->Any:
        return self._other_value(other) // self.value
    
    def __ifloordiv__(self, other:Any)->Any:
        self.value //= self._other_value(other)
        return self.value

    def __mod__(self, other:Any)->Any:
        return self.value % self._other_value(other)
    
    def __rmod__(self, other:Any)->Any:
        return self._other_value(other) % self.value
    
    def __imod__(self, other:Any)->Any:
        self.value %= self._other_value(other)
        return self.value

    def __pow__(self, other:Any)->Any:
        return self.value ** self._other_value(other)
    
    def __rpow__(self, other:Any)->Any:
        return self._other_value(other) ** self.value
    
    def __ipow__(self, other:Any)->Any:
        self.value **= self._other_value(other)
        return self.value

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

    def __getattr__(self, name:str)->Attribute:
        return self._children[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if name in Attribute.__basic_attrs:
            super().__setattr__(name, value)
        else:
            if name not in self._children:
                if not self._extentable:
                    raise AttributeError(f"{self._name} is not extentable")

                self._children[name] = Attribute(self._type_name, self._name + ":" + name)

            self._children[name].value = value