from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token
from ..common import SchemaKind, Axis
from ..gf import float3
from typing import List


class Cone(Gprim):
    """Defines a primitive cone, centered at the origin, whose spine
    is along the specified \\em axis, with the apex of the cone pointing
    in the direction of the positive axis.
    
    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds."""
    
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": True
            }
        }
    }

    height: Attribute[double] = Attribute(double, "height", value=2.0, doc=
        """The length of the cone's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
    )

    radius: Attribute[double] = Attribute(double, "radius", value=1.0, doc=
        """The radius of the cone.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
    )

    axis: Attribute[Axis] = Attribute(Axis, value=Axis.Z, uniform=True,
        doc = "The axis along which the spine of the cone is aligned"
    )

    extent: Attribute[List[float3]] = Attribute(List[float3], value=[(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)], doc=
        """Extent is re-defined on Cone only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
    )
