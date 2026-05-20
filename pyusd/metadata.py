from __future__ import annotations
from typing import List, Dict, Any
from typeguard import typechecked
import copy

from .utils import usd_value_str, infer_type, usd_type_str, in_annotations
from .dtypes import dictionary


class Metadata:

    _parent: Any
    _builtin_data: Dict[str, Any]
    _custom_data: Dict[str, Any]
    _builtin_is_set: Dict[str, bool]
    _custom_is_set: Dict[str, bool]

    def __init__(self, parent:Any=None, kwargs:Dict[str, Any]={})->None:
        self._parent = parent
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

    def clone(self)->Metadata:
        result = Metadata()
        result._builtin_data = copy.deepcopy(self._builtin_data)
        result._custom_data = copy.deepcopy(self._custom_data)
        result._builtin_is_set = copy.deepcopy(self._builtin_is_set)
        result._custom_is_set = copy.deepcopy(self._custom_is_set)
        return result

    @typechecked
    def update(self, kwargs:Dict[str, Any])->None:
        for key, value in kwargs.items():
            if key == "customData":
                for sub_key, sub_value in value.items():
                    if sub_value is None and sub_key in self._custom_data and self._custom_data[sub_key] is not None:
                        pass
                    else:
                        if sub_key in self._custom_data and isinstance(self._custom_data[sub_key], dict):
                            dictionary.update(self._custom_data[sub_key], sub_value)
                        else:
                            self._custom_data[sub_key] = sub_value

                    if sub_key not in self._custom_is_set:
                        self._custom_is_set[sub_key] = False
            else:
                if value is None and key in self._builtin_data and self._builtin_data[key] is not None:
                    pass
                else:
                    if key in self._builtin_data and isinstance(self._builtin_data[key], dict) and isinstance(value, dict):
                        dictionary.update(self._builtin_data[key], value)
                    else:
                        self._builtin_data[key] = value

                if key not in self._builtin_is_set:
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
    def to_str(self, indents:int=0, full:bool=False)->str:
        from .prim import Prim

        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)
        next2_tabs = "    " * (indents + 2)
        result = "(\n"
        
        builtin_str_list:List[str] = []
        for key, value in self._builtin_data.items():
            is_ref = key in ["inherits", "references", "payloads", "specializes", "subLayers"]
            use_ori_value = True
            ori_value = value
            if not full and not self._builtin_is_set[key]:
                if not is_ref:
                    continue
                use_ori_value = False

            if value is None:
                continue

            if key == "doc" and isinstance(value, str) and value == "":
                continue
            
            if key == "inherits":
                value = self._parent._inherits
            elif key == "references":
                value = self._parent._references
            elif key == "payloads":
                value = self._parent._payloads
            elif key == "specializes":
                value = self._parent._specializes
            elif key == "subLayers":
                value = self._parent._sub_layers

            if is_ref and use_ori_value:
                value += ori_value

            if is_ref and not value:
                continue

            rel_layer = None
            if self._parent is not None and isinstance(self._parent, Prim) and self._parent.layer is not None:
                rel_layer = self._parent.layer

            value_str = usd_value_str(value, indents+1, degenerate_list=(is_ref and key != "subLayers"), rel_layer=rel_layer, need_quote=(not is_ref))
            if is_ref and key != "subLayers":
                builtin_str_list.append(f"{next_tabs}prepend {key} = {value_str}")
            else:
                builtin_str_list.append(f"{next_tabs}{key} = {value_str}")
            
        custom_str_list:List[str] = []
        for key, value in self._custom_data.items():
            if not full and not self._custom_is_set[key]:
                continue

            if value is None:
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
