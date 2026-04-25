from typing import Tuple, List, Dict, Any, Set
from typeguard import typechecked

from .utils import usd_value_str


class Metadata:

    _basic_attrs = {
        "_builtin_data",
        "_custom_data",
        "_ignored_data"
    }

    def __init__(self, *args:Tuple[str], **kwargs:Dict[str, Any])->None:
        self._builtin_data:Dict[str, Any] = {}

        for key in args:
            self._builtin_data[key] = None

        for key, value in kwargs.items():
            if key == "customData":
                continue

            self._builtin_data[key] = value

        self._custom_data:Dict[str, Any] = {}
        if "customData" in kwargs:
            self._custom_data = kwargs["customData"]

        self._builtin_data["doc"] = None
        self._ignored_data:Set[str] = {
            "specifier", "typeName", "doc"
        }

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
            if value is None or key in self._ignored_data:
                continue
            
            result_list.append(f"{next_tabs}{key} = {usd_value_str(value)}")

        if len(result_list) > 0:
            result += "\n".join(result_list) + "\n"

        if len(self._custom_data) > 0:
            result += f"{next_tabs}customData = " + usd_value_str(self._custom_data, indents+1) + "\n"

        result += f"{tabs})"

        if len(result_list) == 0 and len(self._custom_data) == 0:
            return ""

        return result
