from typing import List

from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim


class Cube(Gprim):
    """Defines a primitive rectilinear cube centered at the origin.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds.
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": True
            }
        }
    }

    size: AttributeSpec[double] = AttributeSpec(double,
        doc="""Indicates the length of each edge of the cube.  If you
        author \\em size you must also author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    extent: AttributeSpec[List[float3]] = AttributeSpec(List[float3],
        value=[],
        doc="""Extent is re-defined on Cube only to provide a fallback value.
        \\sa UsdGeomGprim::GetExtentAttr().
        """
    )
