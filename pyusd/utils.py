from typing import Any


def usd_value_str(value:Any, indents:int=0, degenerate_list:bool=False):
    from .gf import genType
    from .prim import Prim

    if isinstance(value, genType):
        return value.value_str(indents)
    elif isinstance(value, dict):
        if len(value) == 0:
            return "{}"
        
        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)
        result = "{\n"
        for key, subvalue in value.items():
            subvalue_str = usd_value_str(subvalue, indents + 1)
            if isinstance(key, str):
                result += f"{next_tabs}{usd_type_str(type(subvalue))} {key} = {subvalue_str}\n"
            else:
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
            if degenerate_list:
                return usd_value_str(value[0], indents)
            else:
                return f"{left_bracket}{usd_value_str(value[0], indents + 1)}{right_bracket}"
        else:
            result = f"{left_bracket}\n"
            for subvalue in value:
                subvalue_str = usd_value_str(subvalue, indents + 1)
                result += f"{next_tabs}{subvalue_str}\n"
            result += f"{tabs}{right_bracket}"
        return result
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, Prim):
        return f"<{value.path}>"
    else:
        return str(value)
    
def usd_type_str(type_:type)->str:
    if type_ == str:
        return "string"
    elif type_ == float:
        return "double"
    elif type_ == dict:
        return "dictionary"
    else:
        return type_.__name__