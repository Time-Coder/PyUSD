import os
import re
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Optional,
    Tuple,
    get_args,
    get_origin,
)

import numpy as np

from .dtypes import (
    asset,
    dictionary,
    double,
    group,
    half,
    int64,
    namespace,
    opaque,
    pathExpression,
    string,
    timecode,
    token,
    uchar,
    uint,
    uint64,
)

if TYPE_CHECKING:
    # Only needed for annotations: utils is imported by these modules, so a
    # runtime import here would be circular.
    from .layer import Layer
    from .prim_spec import PrimSpec
from .gf import (
    color3d,
    color3f,
    color3h,
    color4d,
    color4f,
    color4h,
    double2,
    double3,
    double4,
    float2,
    float3,
    float4,
    frame4d,
    half2,
    half3,
    half4,
    int2,
    int3,
    int4,
    matrix2d,
    matrix3d,
    matrix4d,
    normal3d,
    normal3f,
    normal3h,
    point3d,
    point3f,
    point3h,
    quatd,
    quatf,
    quath,
    texCoord2d,
    texCoord2f,
    texCoord2h,
    texCoord3d,
    texCoord3f,
    texCoord3h,
    vector3d,
    vector3f,
    vector3h,
)

usd_scalar_types = (
    bool,
    double,
    float,
    half,
    int,
    int64,
    asset,
    str,
    string,
    token,
    pathExpression,
    timecode,
    uchar,
    uint,
    uint64,
    opaque,
    group
)

usd_vector_types = (
    int2, int3, int4,
    half2, half3, half4,
    float2, float3, float4,
    double2, double3, double4,
    color3h, color3f, color3d,
    color4h, color4f, color4d,
    point3h, point3f, point3d,
    normal3h, normal3f, normal3d,
    vector3h, vector3f, vector3d,
    texCoord2f, texCoord2h, texCoord2d,
    texCoord3f, texCoord3h, texCoord3d,
)

usd_matrix_types = (
    matrix2d, matrix3d, matrix4d, frame4d
)

usd_quat_types = (
    quath, quatf, quatd
)

usd_dtypes = (
    namespace,
    dictionary,
    dict,
    *usd_scalar_types,
    *usd_vector_types,
    *usd_matrix_types,
    *usd_quat_types
)

allowed_types = usd_dtypes + (tuple,)

TYPE_PRIORITY = { int: 1, float: 2 }
NUMPY_TO_PY_TYPE_MAP = {
    np.dtype(np.int8): int,
    np.dtype(np.int16): int,
    np.dtype(np.int32): int,
    np.dtype(np.int64): int64,
    np.dtype(np.uint8): uchar,
    np.dtype(np.uint16): int,
    np.dtype(np.uint32): int,
    np.dtype(np.uint64): uint64,
    np.dtype(np.float16): half,
    np.dtype(np.float32): float,
    np.dtype(np.float64): double,
    np.dtype(np.bool_): bool,
    np.dtype(float2): float2,
    np.dtype(float3): float3,
    np.dtype(float4): float4,
    np.dtype(double2): double2,
    np.dtype(double3): double3,
    np.dtype(double4): double4,
    np.dtype(int2): int2,
    np.dtype(int3): int3,
    np.dtype(int4): int4,
    np.dtype(quatf): quatf,
    np.dtype(quatd): quatd,
}

def _to_abs(match: re.Match):
    relative_path = match.group(1)
    absolute_path = os.path.abspath(relative_path).replace("\\", "/")
    return f"@{absolute_path}@"

asset_pattern = re.compile(r"@(.*?)@")

def abspath(text):
    if "@" not in text:
        return os.path.abspath(text).replace("\\", "/")

    return asset_pattern.sub(_to_abs, text)

def analyze_list_type(type_hint):
    depth = 0
    current_type = type_hint

    while True:
        origin = get_origin(current_type)

        if origin is list:
            args = get_args(current_type)
            if not args:
                raise TypeError("no element type int List")

            inner_type = args[0]
            inner_origin = get_origin(inner_type)

            if (
                inner_origin is not None
                and inner_origin is not list
                and inner_origin in [dict, tuple, set, frozenset]
            ):
                raise TypeError(f"not support type {inner_origin}")

            depth += 1
            current_type = inner_type
        else:
            break

    return current_type, depth

def _analyze_type(item: Any) -> Tuple[int, type]:
    if isinstance(item, list):
        if not item:
            return 1, Any

        children_results = [_analyze_type(elem) for elem in item]
        first_depth, _ = children_results[0]

        if any(depth != first_depth for depth, _ in children_results):
            raise TypeError("list dimension not match")

        child_types = [t for _, t in children_results]
        unique_types = set(child_types)

        final_type = None
        if len(unique_types) == 1:
            final_type = child_types[0]
        elif unique_types.issubset({int, float}):
            final_type = max(unique_types, key=lambda t: TYPE_PRIORITY.get(t, 0))
        else:
            raise TypeError(f"list type not compatible: {unique_types}")

        return first_depth + 1, final_type

    elif isinstance(item, np.ndarray):
        py_equiv_type = NUMPY_TO_PY_TYPE_MAP.get(item.dtype, item.dtype)

        if not issubclass(py_equiv_type, allowed_types):
            pass

        return 0, py_equiv_type

    else:
        val_type = type(item)
        if not issubclass(val_type, allowed_types):
            raise TypeError(f"not supported type: {val_type}")

        if val_type is float:
            val_type = double

        return 0, val_type

def infer_type(data: Any) -> type:
    from .data import Data

    if isinstance(data, Data):
        return data.type

    if isinstance(data, np.ndarray):
        if data.dtype == np.object_:
            pass

        depth, _ = _analyze_type(data)
        target_type = NUMPY_TO_PY_TYPE_MAP.get(data.dtype, data.dtype)

        ndim = data.ndim
        result: Any = target_type
        for _ in range(ndim):
            result = List[result]
        return result

    depth, element_type = _analyze_type(data)

    if depth == 0:
        return element_type

    current_type: Any = element_type
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


def in_annotations(name:str, cls:type)->bool:
    for klass in cls.__mro__:
        if hasattr(klass, '__annotations__') and name in klass.__annotations__:
            return True

    return False


def camel_to_snake(name: str) -> str:
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def snake_to_pascal(name: str) -> str:
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    return ''.join(word.capitalize() for word in name.split('_'))


# --- paths -----------------------------------------------------------------
#
# The whole path-helper family lives together here because they are mutually
# recursive and are consumed from prim, stage, layer, and composition alike.
# The USD path grammar is only partly implemented; see core_spec.md for the
# escaping, XID, and expression rules still to cover.


def path_from_reference_text(text: str) -> str:
    text = str(text).strip()
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1]

    return text


def normalize_prim_path(path: str) -> str:
    if path is None:
        raise ValueError("path cannot be None")

    path = str(path).strip()
    if not path or path == "/":
        return "/"

    path = path_from_reference_text(path)
    if not path.startswith("/"):
        path = "/" + path

    while "//" in path:
        path = path.replace("//", "/")

    if len(path) > 1:
        path = path.rstrip("/")

    return path


def normalize_property_name(name: str) -> str:
    return str(name).strip().replace(".", ":")


def path_items(path: str) -> List[str]:
    path = normalize_prim_path(path)
    if path == "/":
        return []

    return path.strip("/").split("/")


def ancestors(path: str) -> List[str]:
    parts = path_items(path)
    result: List[str] = []
    for index in range(len(parts)):
        result.append("/" + "/".join(parts[: index + 1]))

    return result


def path_is_under(path: str, prefix: str) -> bool:
    path = normalize_prim_path(path)
    prefix = normalize_prim_path(prefix)
    return path == prefix or path.startswith(prefix + "/")


def path_suffix(prefix: str, path: str) -> str:
    prefix = normalize_prim_path(prefix)
    path = normalize_prim_path(path)
    if prefix == path:
        return ""

    if path.startswith(prefix + "/"):
        return path[len(prefix) + 1 :]

    return ""


def join_path(base: str, suffix: str) -> str:
    base = normalize_prim_path(base)
    suffix = str(suffix).strip("/")
    if not suffix:
        return base

    if base == "/":
        return normalize_prim_path("/" + suffix)

    return normalize_prim_path(base + "/" + suffix)


def join_relative_path(base_path: str, path: str) -> str:
    base_path = normalize_prim_path(base_path) if base_path else ""
    path = str(path)
    if path.startswith("/"):
        return normalize_prim_path(path)

    if not base_path or base_path == "/":
        return normalize_prim_path("/" + path)

    return normalize_prim_path(base_path + "/" + path)


def prim_descendant(prim: "PrimSpec", suffix: str) -> Optional["PrimSpec"]:
    """Descend a storage prim by relative path, without touching the engine."""
    suffix = str(suffix).strip("/")
    if not suffix:
        return prim

    current = prim
    for item in suffix.split("/"):
        if item not in current._children:
            return None

        current = current._children[item]

    return current


def prim_at(layer: "Layer", path: str) -> Optional["PrimSpec"]:
    """The authored storage prim at ``path`` within one layer, if it defines one."""
    parts = path_items(path)
    if not parts:
        return None

    prim = layer._root_prims.get(parts[0])
    if prim is None:
        return None

    return prim_descendant(prim, "/".join(parts[1:]))
