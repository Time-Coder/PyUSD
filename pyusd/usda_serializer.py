from __future__ import annotations
from typing import Any, Optional, Union, TYPE_CHECKING

from .utils import analyze_list_type, infer_type

if TYPE_CHECKING:
    from .layer import Layer


class UsdaSerializer:

    @staticmethod
    def value_str(value:Any, indents:int=0, degenerate_list:bool=False, rel_layer:Optional[Union[str, Layer]]="", need_quote:bool=True, is_relocates:bool=False)->str:
        from .data import Data
        from .gf import genType, MathForm
        from .layer import Layer
        from .prim import PrimSpec
        from .dtypes import asset

        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)

        if isinstance(value, genType):
            if value.math_form == MathForm.Mat:
                result = "(\n"
                for i in range(value.shape[0]):
                    result += f"{next_tabs}("
                    for j in range(value.shape[1]):
                        result += str(value[i, j])
                        if j != value.shape[1] - 1:
                            result += ", "
                    result += ")"
                    if i != value.shape[0] - 1:
                        result += ",\n"
                    else:
                        result += "\n"
                result += f"{tabs})"
                return result
            else:
                return f"({', '.join([UsdaSerializer.value_str(sub_value) for sub_value in value])})"
        elif isinstance(value, dict):
            if len(value) == 0:
                return "{}"

            result = "{\n"
            for key, subvalue in value.items():
                subvalue_str = UsdaSerializer.value_str(subvalue, indents + 1, degenerate_list=degenerate_list, rel_layer=rel_layer, need_quote=need_quote)
                if isinstance(key, str):
                    result += f"{next_tabs}{UsdaSerializer.type_str(infer_type(subvalue))} {key} = {subvalue_str}\n"
                else:
                    if isinstance(key, PrimSpec):
                        key = f"<{key.path}>"
                        
                    result += f"{next_tabs}{key}: {subvalue_str}\n"
            result += f"{tabs}}}"
            return result
        elif isinstance(value, list) or isinstance(value, tuple):
            if isinstance(value, list):
                left_bracket = "["
                right_bracket = "]"
            elif isinstance(value, tuple):
                left_bracket = "("
                right_bracket = ")"

            if len(value) == 0:
                return f"{left_bracket}{right_bracket}"

            tabs = "    " * indents
            next_tabs = "    " * (indents + 1)
            if len(value) == 1:
                result = UsdaSerializer.value_str(value[0], indents+1, degenerate_list=degenerate_list, rel_layer=rel_layer, need_quote=need_quote)
                if degenerate_list:
                    return result
                else:
                    if "\n" not in result and len(result) < 100:
                        return f"{left_bracket}{result}{right_bracket}"
                    else:
                        return f"{left_bracket}\n{next_tabs}{result}\n{right_bracket}"
            else:
                result_list = [UsdaSerializer.value_str(subvalue, indents+1, degenerate_list=degenerate_list, rel_layer=rel_layer, need_quote=need_quote) for subvalue in value]
                result = ", ".join(result_list)
                if "\n" not in result and len(result) < 100:
                    return f"{left_bracket}{result}{right_bracket}"

                result = f"{left_bracket}\n"
                result += f",\n{next_tabs}".join(result_list)
                result += f"\n{tabs}{right_bracket}"
            return result
        elif isinstance(value, Data):
            return UsdaSerializer.value_str(value.value)
        elif isinstance(value, asset):
            return f'@{value}@'
        elif isinstance(value, (PrimSpec, Layer)):
            return value.id(rel_layer)
        elif isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            else:
                return str(value)
        elif isinstance(value, bool):
            return ("true" if value else "false")
        elif isinstance(value, str):
            value = value.replace("\\", "\\\\")
            if "\n" in value:
                return f'"""{value}"""'
            else:
                if need_quote:
                    return f'"{value}"'
                else:
                    return value
        else:
            return str(value)

    @staticmethod
    def type_str(type_:type, array_dim:int=0)->str:
        from .dtypes import token
        
        dtype, dim = analyze_list_type(type_)
        array_dim += dim

        result = ""
        if dtype == str:
            result = "string"
        elif dtype == dict:
            result = "dictionary"
        elif issubclass(dtype, token):
            result = "token"
        else:
            result = dtype.__name__

        result += "[]" * array_dim
        return result
