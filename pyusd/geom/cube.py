from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double
from ..common import SchemaKind
from ..gf import float3
from typing import List


class Cube(Gprim):
    """Defines a primitive rectilinear cube centered at the origin.
    
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

    size: Attribute[double] = Attribute(double, "size", value=2.0, doc=
        """Indicates the length of each edge of the cube.  If you
        author \\em size you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
    )

    extent: Attribute[List[float3]] = Attribute(List[float3], value=[(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)], doc=
        """Extent is re-defined on Cube only to provide a fallback value.
        \\sa UsdGeomGprim::GetExtentAttr()."""
    )
