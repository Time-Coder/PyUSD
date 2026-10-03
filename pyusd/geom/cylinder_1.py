from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis, SchemaKind
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim


class Cylinder_1(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis, with a pair of radii
    describing the size of the end points.

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
        doc="""The length of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    radiusTop: AttributeSpec[double] = AttributeSpec(double,
        doc="""The radius of the top of the cylinder - i.e. the face located
        along the positive \\em axis. If you author \\em radiusTop you must also
        author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    radiusBottom: AttributeSpec[double] = AttributeSpec(double,
        doc="""The radius of the bottom of the cylinder - i.e. the face
        point located along the negative \\em axis. If you author
        \\em radiusBottom you must also author \\em extent.

        \\sa GetExtentAttr()
        """
    )

    axis: AttributeSpec[Axis] = AttributeSpec(Axis, uniform=True, doc="The axis along which the spine of the cylinder is aligned")

    extent: AttributeSpec[List[float3]] = AttributeSpec(List[float3],
        value=[],
        doc="""Extent is re-defined on Cylinder only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr().
        """
    )
