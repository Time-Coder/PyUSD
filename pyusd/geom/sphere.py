from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double
from ..common import SchemaKind
from ..gf import float3
from typing import List


class Sphere(Gprim):
    """Defines a primitive sphere centered at the origin.
    
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

    radius: Attribute[double] = Attribute(double, "radius", value=1.0, doc=
        """Indicates the sphere's radius.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
    )

    extent: Attribute[List[float3]] = Attribute(List[float3], value=[(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)], doc=
        """Extent is re-defined on Sphere only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
    )
