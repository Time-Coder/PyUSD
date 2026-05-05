from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class RiSplineAPI(APISchemaBase):
    """
    \\deprecated This API schema will be removed in a future release.
    
    RiSplineAPI is a general purpose API schema used to describe
    a named spline stored as a set of attributes on a prim.
    
    It is an add-on schema that can be applied many times to a prim with
    different spline names. All the attributes authored by the schema
    are namespaced under "$NAME:spline:", with the name of the
    spline providing a namespace for the attributes.
    
    The spline describes a 2D piecewise cubic curve with a position and
    value for each knot. This is chosen to give straightforward artistic
    control over the shape. The supported basis types are:
    
    - linear (UsdRiTokens->linear)
    - bspline (UsdRiTokens->bspline)
    - Catmull-Rom (UsdRiTokens->catmullRom)
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "SplineAPI"
        }
    }
