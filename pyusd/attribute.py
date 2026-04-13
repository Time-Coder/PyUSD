from typing import Dict, Any, Tuple

from .gf import double2, double3, double4, float2, float3, float4, int2, int3, int4, matrix2d, matrix3d, matrix4d


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
        "matrix4d": matrix4d
    }

    def __init__(self, type_name:str, name:str)->None:
        self._type_name:str = type_name
        self._name:str = name
        self._time_samples:Dict[float, Any] = {}
        self._value:Any = None

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
        self._value = value

    def to_str(self, indents:int=0)->str:
        tabs = "    " * indents
        return f"{tabs}{self._type_name} {self._name} = {self._value}"