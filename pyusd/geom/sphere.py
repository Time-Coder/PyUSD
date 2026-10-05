from typing import List

from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim


class Sphere(Gprim):
    """Defines a primitive sphere centered at the origin.

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

    radius: AttributeSpec[double] = AttributeSpec(double,
        value=1.0,
        doc="""Indicates the sphere's radius.  If you
        author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    extent: AttributeSpec[List[float3]] = AttributeSpec(List[float3],
        value=[(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)],
        doc="""Extent is re-defined on Sphere only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr().
        """
    )
