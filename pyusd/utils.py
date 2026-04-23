from typing import List, Any, Set, get_origin, get_args, Optional

import numpy as np

from .gf import double2, double3, double4, float2, float3, float4, int2, int3, int4, matrix2d, matrix3d, matrix4d, quatf, quatd
from .dtypes import double, half, int64, string, token, timecode, uchar, uint, uint64, namespace


usd_scalar_types = {
    bool,
    double,
    float,
    half,
    int,
    int64,
    string,
    token,
    timecode,
    uchar,
    uint,
    uint64
}

usd_vector_types = {
    double2,
    double3,
    double4,
    float2,
    float3,
    float4,
    int2,
    int3,
    int4
}

usd_matrix_types = {
    matrix2d,
    matrix3d,
    matrix4d
}

usd_quat_types = {
    quatf,
    quatd
}

usd_dtypes = {
    namespace,
    *usd_scalar_types,
    *usd_vector_types,
    *usd_matrix_types,
    *usd_quat_types
}

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
                result += f"{next_tabs}{usd_type_str(infer_type(subvalue))} {key} = {subvalue_str}\n"
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
            for i, subvalue in enumerate(value):
                subvalue_str = usd_value_str(subvalue, indents + 1)
                result += f"{next_tabs}{subvalue_str}"
                result += (",\n" if i < len(value) - 1 else "\n")
            result += f"{tabs}{right_bracket}"
        return result
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, Prim):
        return f"<{value.path}>"
    elif isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        else:
            return str(value)
    else:
        return str(value)
    
def usd_type_str(type_:type, array_dim:int=0)->str:
    dtype, dim = analyze_list_type(type_)
    array_dim += dim

    result = ""
    if dtype == str:
        result = "string"
    elif dtype == float:
        result = "double"
    elif dtype == dict:
        result = "dictionary"
    else:
        result = dtype.__name__

    result += "[]" * array_dim
    return result

def analyze_list_type(type_hint):
    depth = 0
    current_type = type_hint
    
    while True:
        origin = get_origin(current_type)
        
        if origin is list:
            args = get_args(current_type)
            if not args:
                raise TypeError(f"no element type int List")
            
            inner_type = args[0]
            inner_origin = get_origin(inner_type)
            
            if inner_origin is not None and inner_origin is not list:
                if inner_origin in [dict, tuple, set, frozenset]:
                    raise TypeError(f"not support type {inner_origin}")
            
            depth += 1
            current_type = inner_type
        else:
            break

    return current_type, depth

def infer_type(data: Any, allowed_types: Optional[Set[type]] = None) -> str:
    if allowed_types is None:
        allowed_types = usd_dtypes | { tuple }

    TYPE_PRIORITY = { int: 1, float: 2 }
    NUMPY_TO_PY_TYPE_MAP = {
        np.int8: int, np.int16: int, np.int32: int, np.int64: int,
        np.uint8: int, np.uint16: int, np.uint32: int, np.uint64: int,
        np.float16: float, np.float32: float, np.float64: float,
        np.bool_: bool
    }

    def _analyze(item: Any) -> tuple:
        if isinstance(item, list):
            if not item: return 1, Any, None
            
            children_results = [_analyze(elem) for elem in item]
            first_depth, first_type, _ = children_results[0]
            
            if any(depth != first_depth for depth, _, _ in children_results):
                raise TypeError("list dimension not match")
            
            child_types = [t for _, t, _ in children_results]
            unique_types = set(child_types)
            
            final_type = None
            if len(unique_types) == 1:
                final_type = child_types[0]
            elif unique_types.issubset({int, float}):
                final_type = max(unique_types, key=lambda t: TYPE_PRIORITY.get(t, 0))
            else:
                raise TypeError(f"list type not compatible: {unique_types}")
                
            return first_depth + 1, final_type, None

        elif isinstance(item, np.ndarray):
            py_equiv_type = NUMPY_TO_PY_TYPE_MAP.get(item.dtype.type, item.dtype.type)
            
            if py_equiv_type not in allowed_types:
                 pass 
            
            return 0, py_equiv_type, item.dtype

        else:
            val_type = type(item)
            if val_type not in allowed_types:
                raise TypeError(f"not supported type: {val_type}")
            return 0, val_type, None

    if isinstance(data, np.ndarray):
        if data.dtype == np.object_:
             pass 
        
        depth, elem_type, dtype_obj = _analyze(data)
        target_type = NUMPY_TO_PY_TYPE_MAP.get(data.dtype.type, data.dtype.type)
        
        ndim = data.ndim
        result = target_type
        for _ in range(ndim):
            result = List[result]
        return result

    depth, element_type, _ = _analyze(data)
    
    if depth == 0:
        return element_type
    
    current_type = element_type
    for _ in range(depth):
        current_type = List[current_type]
        
    return current_type

def nest_map(nested_list, func):
    if not isinstance(nested_list, list):
        return func(nested_list)

    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.append(nest_map(item, func))
        else:
            result.append(func(item))

    return result
