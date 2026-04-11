from typing import Dict, Any


class Attribute:

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