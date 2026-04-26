from .curves import Curves
from ..attribute import Attribute
from ..gf import vector3f
from typing import List


class HermiteCurves(Curves):
    "This schema specifies a cubic hermite interpolated curve batch as\n    sometimes used for defining guides for animation. While hermite curves can\n    be useful because they interpolate through their control points, they are\n    not well supported by high-end renderers for imaging. Therefore, while we\n    include this schema for interchange, we strongly recommend the use of\n    UsdGeomBasisCurves as the representation of curves intended to be rendered\n    (ie. hair or grass). Hermite curves can be converted to a Bezier\n    representation (though not from Bezier back to Hermite in general).\n\n    \\section UsdGeomHermiteCurves_Interpolation Point Interpolation\n    \n    The initial cubic curve segment is defined by the first two points and\n    first two tangents. Additional segments are defined by additional \n    point / tangent pairs.  The number of segments for each non-batched hermite\n    curve would be len(curve.points) - 1.  The total number of segments\n    for the batched UsdGeomHermiteCurves representation is\n    len(points) - len(curveVertexCounts).\n\n    \\section UsdGeomHermiteCurves_Primvars Primvar, Width, and Normal Interpolation\n\n    Primvar interpolation is not well specified for this type as it is not\n    intended as a rendering representation. We suggest that per point\n    primvars would be linearly interpolated across each segment and should \n    be tagged as 'varying'.\n\n    It is not immediately clear how to specify cubic or 'vertex' interpolation\n    for this type, as we lack a specification for primvar tangents. This\n    also means that width and normal interpolation should be restricted to\n    varying (linear), uniform (per curve element), or constant (per prim).\n    "
    def __init__(self, name:str="")->None: ...

    @property
    def tangents(self)->Attribute[List[vector3f]]:
        'Defines the outgoing trajectory tangent for each point. \n                 Tangents should be the same size as the points attribute.'


    @tangents.setter
    def tangents(self, value:List[vector3f])->None: ...
