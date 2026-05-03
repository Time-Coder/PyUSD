from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double
from ..common import SchemaKind, Axis
from ..gf import float3
from typing import List


class Cylinder_1(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis, with a pair of radii
    describing the size of the end points.

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

    height: Attribute[double] = Attribute(double, "height", value=2, doc=
        """The length of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()"""
    )

    radiusTop: Attribute[double] = Attribute(double, "radiusTop", value=1.0, doc=
        """The radius of the top of the cylinder - i.e. the face located
        along the positive \\em axis. If you author \\em radiusTop you must also
        author \\em extent.

        \\sa GetExtentAttr()"""
    )

    radiusBottom: Attribute[double] = Attribute(double, "radiusBottom", value=1.0, doc=
        """The radius of the bottom of the cylinder - i.e. the face
        point located along the negative \\em axis. If you author
        \\em radiusBottom you must also author \\em extent.

        \\sa GetExtentAttr()"""
    )

    axis: Attribute[Axis] = Attribute(Axis, value=Axis.Z, uniform=True,
        doc="The axis along which the spine of the cylinder is aligned"
    )

    extent: Attribute[List[float3]] = Attribute(List[float3], value=[(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)], doc=
        """Extent is re-defined on Cylinder only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
    )
