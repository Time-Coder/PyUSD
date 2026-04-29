from .curves import Curves
from ..attribute import Attribute
from ..gf import vector3f
from ..common import SchemaKind
from typing import List


class HermiteCurves(Curves):
    """This schema specifies a cubic hermite interpolated curve batch as
    sometimes used for defining guides for animation. While hermite curves can
    be useful because they interpolate through their control points, they are
    not well supported by high-end renderers for imaging. Therefore, while we
    include this schema for interchange, we strongly recommend the use of
    UsdGeomBasisCurves as the representation of curves intended to be rendered
    (ie. hair or grass). Hermite curves can be converted to a Bezier
    representation (though not from Bezier back to Hermite in general).

    \\section UsdGeomHermiteCurves_Interpolation Point Interpolation
    
    The initial cubic curve segment is defined by the first two points and
    first two tangents. Additional segments are defined by additional 
    point / tangent pairs.  The number of segments for each non-batched hermite
    curve would be len(curve.points) - 1.  The total number of segments
    for the batched UsdGeomHermiteCurves representation is
    len(points) - len(curveVertexCounts).

    \\section UsdGeomHermiteCurves_Primvars Primvar, Width, and Normal Interpolation

    Primvar interpolation is not well specified for this type as it is not
    intended as a rendering representation. We suggest that per point
    primvars would be linearly interpolated across each segment and should 
    be tagged as 'varying'.

    It is not immediately clear how to specify cubic or 'vertex' interpolation
    for this type, as we lack a specification for primvar tangents. This
    also means that width and normal interpolation should be restricted to
    varying (linear), uniform (per curve element), or constant (per prim).
    """
    
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    def __init__(self, name:str="")->None:
        Curves.__init__(self, name)

        self.create_prop(Attribute(List[vector3f], "tangents", value=[], metadata={
            "doc": """Defines the outgoing trajectory tangent for each point. 
                 Tangents should be the same size as the points attribute."""
        }))
