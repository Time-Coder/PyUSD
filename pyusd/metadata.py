from typing import List, Dict, Any
from typeguard import typechecked

from .utils import usd_value_str


class Metadata:

    _basic_attrs = {
        "_builtin_data",
        "_custom_data"
    }

    @typechecked
    def __init__(self, *builtin_keys:List[str])->None:
        self._builtin_data:Dict[str, Any] = {}
        for key in builtin_keys:
            self._builtin_data[key] = None

        self._custom_data:Dict[str, Any] = {}

    @typechecked
    def __getattr__(self, name:str)->Any:
        if name in self._builtin_data:
            return self._builtin_data[name]
        elif name in self._custom_data:
            return self._custom_data[name]
        else:
            raise AttributeError(f"current metadata has no attribute '{name}'")
    
    @typechecked
    def __setattr__(self, name:str, value:Any)->None:
        if name in self._basic_attrs:
            super().__setattr__(name, value)
        elif name in self._builtin_data:
            self._builtin_data[name] = value
        else:
            self._custom_data[name] = value

    @property
    def customData(self)->Dict[str, Any]:
        return self._custom_data

    @typechecked
    def to_str(self, indents:int=0)->str:
        if len(self._builtin_data) == 0 and len(self._custom_data) == 0:
            return ""
        
        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)
        result = "(\n"
        
        result_list:List[str] = []
        for key, value in self._builtin_data.items():
            if value is None:
                continue
            
            result_list.append(f"{next_tabs}{key} = {usd_value_str(value)}")

        if len(result_list) > 0:
            result += "\n".join(result_list) + "\n"

        if len(self._custom_data) > 0:
            result += f"{next_tabs}customData = " + usd_value_str(self._custom_data, indents+1)

        result += f"\n{tabs})"

        if len(result_list) == 0 and len(self._custom_data) == 0:
            return ""

        return result
