from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token
from ..common import SchemaKind, Axis
from ..gf import float3
from typing import List


class Plane(Gprim):
    """Defines a primitive plane, centered at the origin, and is defined by
    a cardinal axis, width, and length. The plane is double-sided by default.

    The axis of width and length are perpendicular to the plane's \\em axis:

    axis  | width  | length
    ----- | ------ | -------
    X     | z-axis | y-axis
    Y     | x-axis | z-axis
    Z     | x-axis | y-axis

    """
    
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": True
            }
        }
    }

    doubleSided: Attribute[bool] = Attribute(bool, value=True, uniform=True, doc=
        """Planes are double-sided by default. Clients may also support
        single-sided planes.

        \\sa UsdGeomGprim::GetDoubleSidedAttr()"""
    )

    width: Attribute[double] = Attribute(double, value=2.0, doc=
        """The width of the plane, which aligns to the x-axis when \\em axis is
        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width 
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""
    )

    length: Attribute[double] = Attribute(double, value=2.0, doc=
        """The length of the plane, which aligns to the y-axis when \\em axis is
        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length 
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""
    )

    axis: Attribute[Axis] = Attribute(Axis, value=Axis.Z, uniform=True,
        doc = """The axis along which the surface of the plane is aligned. When set
        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in 
        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.

        \\sa UsdGeomGprim::GetAxisAttr()."""
    )

    extent: Attribute[List[float3]] = Attribute(List[float3], value=[(-1.0, -1.0, 0.0), (1.0, 1.0, 0.0)], doc=
        """Extent is re-defined on Plane only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
    )
