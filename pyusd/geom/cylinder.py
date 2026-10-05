from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis, SchemaKind
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim


class Cylinder(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis.

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

    height: AttributeSpec[double] = AttributeSpec(double,
        value=2,
        doc="""The size of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    radius: AttributeSpec[double] = AttributeSpec(double,
        value=1.0,
        doc="""The radius of the cylinder. If you author \\em radius
        you must also author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    axis: AttributeSpec[Axis] = AttributeSpec(Axis,
        uniform=True,
        value="Z",
        doc="The axis along which the spine of the cylinder is aligned"
    )

    extent: AttributeSpec[List[float3]] = AttributeSpec(List[float3],
        value=[(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)],
        doc="""Extent is re-defined on Cylinder only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr().
        """
    )
