"""Compatibility shim: `pyusd.gf` now re-exports the standalone `pygf` package.

The vector, matrix and quaternion types moved out to `pygf` so that PyUSD,
PyMaterialX and PyRHI can all share them without depending on each other. The
move is mechanical -- `pygf`'s own dynamic type factory resolves module names
relative to its own package (`helper.from_import` passes `package=__package__`),
so nothing inside it had to change but its name.

This module stays so that `from gf import float3` keeps working. It is a
forwarding re-export and nothing else: there is no `pyusd/gf/genVec3.py` behind
it, so `from pyusd.gf.genVec3 import genVec3` -- a submodule import -- does *not*
work. Only the names below resolve.

What that means for each kind of import:

    from gf import float3          works, forwarded
    from gf import funcs          works, `funcs` is a module attribute of pygf
    from gf import genVec3         works, same as the class
    from pyusd.gf.genVec3 import genVec3 fails, no submodule exists

Drop this shim once nothing imports through it, then rename the remaining
`pyusd.gf` references to `pygf` directly. `__all__` is the list of what a caller
is expected to use; anything in `pygf.__all__` resolves here.
"""

# `from pygf import *` is not usable here: a module-level `import *` pulls in
# every name in __all__, but the names have to land in this namespace under their
# own names for `from gf import X` to find them. Importing the names
# explicitly is what makes the forwarding real.
# The abstract intermediates are not all re-exported by pygf's own `__init__`.
# `Vec2Type`/`Vec3Type`/`Vec4Type` live in pygf.genVec2/3/4 and `Mat2Type`/
# `Mat3Type`/`Mat4Type` in pygf.genMat2/3/4, so they are imported from those
# modules directly rather than off the package.
# `funcs` is a module, not a name `pygf.__all__` exports, but `funcs.abs` and
# friends are how the set is reached everywhere in this repository. Importing it
# keeps `from gf import funcs` working, which several call sites use.
from pygf import (
    MathForm,
    MatType,
    Number,
    QuatType,
    VecType,
    # the element-wise function set, and the two helpers from helper.py
    abs,
    acos,
    acosh,
    all,
    any,
    asin,
    asinh,
    atan,
    atanh,
    # vectors
    bool2,
    bool3,
    bool4,
    ceil,
    clamp,
    color3d,
    color3f,
    # USD aliases
    color3h,
    color4d,
    color4f,
    color4h,
    conjugate,
    cos,
    cosh,
    cross,
    determinant,
    distance,
    dot,
    double2,
    double3,
    double4,
    equal,
    exp,
    exp2,
    exp10,
    faceforward,
    float2,
    float3,
    float4,
    floor,
    fract,
    frame4d,
    funcs,
    genMat,
    genMat2,
    genMat3,
    genMat4,
    genQuat,
    genType,
    genVec,
    genVec2,
    genVec3,
    genVec4,
    greaterThan,
    greaterThanEqual,
    half2,
    half3,
    half4,
    int2,
    int3,
    int4,
    inverse,
    inversesqrt,
    length,
    lessThan,
    lessThanEqual,
    log,
    log2,
    log10,
    # matrices
    matrix2b,
    matrix2d,
    matrix2f,
    matrix3b,
    matrix3d,
    matrix3f,
    matrix4b,
    matrix4d,
    matrix4f,
    matrixCompMult,
    max,
    min,
    mix,
    mod,
    normal3d,
    normal3f,
    normal3h,
    normalize,
    not_,
    notEqual,
    outerProduct,
    patch_nparray,
    point3d,
    point3f,
    point3h,
    pow,
    # quaternions
    quatb,
    quatd,
    quatf,
    quath,
    reflect,
    refract,
    round,
    roundEven,
    sign,
    sin,
    sinh,
    sizeof,
    smoothstep,
    sqrt,
    step,
    tan,
    tanh,
    texCoord2d,
    texCoord2f,
    texCoord2h,
    texCoord3d,
    texCoord3f,
    texCoord3h,
    trace,
    transpose,
    trunc,
    uint2,
    uint3,
    uint4,
    vector3d,
    vector3f,
    vector3h,
)
from pygf.genMat2 import Mat2Type
from pygf.genMat3 import Mat3Type
from pygf.genMat4 import Mat4Type
from pygf.genVec2 import Vec2Type
from pygf.genVec3 import Vec3Type
from pygf.genVec4 import Vec4Type

__all__ = [
    "MathForm", "Number", "genType", "patch_nparray", "funcs",
    "genVec", "VecType", "genVec2", "Vec2Type", "genVec3", "Vec3Type", "genVec4", "Vec4Type",
    "genMat", "MatType", "genMat2", "Mat2Type", "genMat3", "Mat3Type", "genMat4", "Mat4Type",
    "genQuat", "QuatType",
    "bool2", "bool3", "bool4",
    "int2", "int3", "int4",
    "uint2", "uint3", "uint4",
    "half2", "half3", "half4",
    "float2", "float3", "float4",
    "double2", "double3", "double4",
    "matrix2b", "matrix3b", "matrix4b",
    "matrix2f", "matrix3f", "matrix4f",
    "matrix2d", "matrix3d", "matrix4d",
    "quatb", "quatf", "quatd", "quath",
    "color3h", "color3f", "color3d",
    "color4h", "color4f", "color4d",
    "texCoord2h", "texCoord2f", "texCoord2d",
    "texCoord3h", "texCoord3f", "texCoord3d",
    "normal3h", "normal3f", "normal3d",
    "point3h", "point3f", "point3d",
    "vector3h", "vector3f", "vector3d",
    "frame4d",

    "abs", "sign", "floor", "ceil", "trunc", "round", "roundEven", "fract", "mod",
    "min", "max", "clamp", "mix", "step", "smoothstep", "sqrt", "inversesqrt",
    "pow", "exp", "exp2", "exp10", "log", "log2", "log10",
    "sin", "cos", "tan", "asin", "acos", "atan",
    "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
    "length", "normalize", "distance", "dot", "cross", "faceforward", "reflect", "refract",
    "transpose", "determinant", "inverse", "trace", "conjugate",
    "matrixCompMult", "outerProduct", "lessThan", "lessThanEqual",
    "greaterThan", "greaterThanEqual", "equal", "notEqual", "any", "all", "not_", "sizeof",
]
