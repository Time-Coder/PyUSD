from typing import List, Dict, Any
from typeguard import typechecked

from .utils import usd_value_str, infer_type, usd_type_str, in_annotations
from .dtypes import dictionary


class Metadata:

    _builtin_data: Dict[str, Any]
    _custom_data: Dict[str, Any]
    _builtin_is_set: Dict[str, bool]
    _custom_is_set: Dict[str, bool]

    def __init__(self, kwargs:Dict[str, Any]={})->None:
        self._builtin_data: Dict[str, Any] = {}
        self._builtin_is_set: Dict[str, bool] = {}
        self._custom_is_set: Dict[str, bool] = {}

        for key, value in kwargs.items():
            if key == "customData":
                if not isinstance(value, dictionary):
                    value = dictionary(value)

                self._custom_data = value
                for sub_key in self._custom_data.keys():
                    self._custom_is_set[sub_key] = False

                continue

            self._builtin_data[key] = value
            self._builtin_is_set[key] = False

        if "customData" not in kwargs:
            self._custom_data = dictionary()

    @typechecked
    def update(self, kwargs:Dict[str, Any])->None:
        for key, value in kwargs.items():
            if key == "customData":
                self._custom_data.update(value)
                for sub_key in self._custom_data.keys():
                    self._custom_is_set[sub_key] = False
            else:
                self._builtin_data[key] = value
                self._builtin_is_set[key] = False

    @property
    def customData(self)->dictionary:
        return self._custom_data

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
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return
        
        if name in self._builtin_data:
            self._builtin_data[name] = value
            self._builtin_is_set[name] = True
        else:
            self._custom_data[name] = value
            self._custom_is_set[name] = True

    @typechecked
    def to_str(self, indents:int=0)->str:        
        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)
        next2_tabs = "    " * (indents + 2)
        result = "(\n"
        
        builtin_str_list:List[str] = []
        for key, value in self._builtin_data.items():
            if not self._builtin_is_set[key]:
                continue
            
            builtin_str_list.append(f"{next_tabs}{key} = {usd_value_str(value, indents+1)}")

        custom_str_list:List[str] = []
        for key, value in self._custom_data.items():
            if not self._custom_is_set[key]:
                continue

            custom_str_list.append(f"{next2_tabs}{usd_type_str(infer_type(value))} {key} = {usd_value_str(value, indents+2)}")

        if len(builtin_str_list) == 0 and len(custom_str_list) == 0:
            return ""

        if builtin_str_list:
            result += "\n".join(builtin_str_list) + "\n"

        if custom_str_list:
            result += f"{next_tabs}customData = {{\n"
            result += "\n".join(custom_str_list)
            result += f"\n{next_tabs}}}\n"

        result += f"{tabs})"

        return result
