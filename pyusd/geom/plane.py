from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis, SchemaKind
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim


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

    doubleSided: AttributeSpec[bool] = AttributeSpec(bool,
        uniform=True,
        doc="""Planes are double-sided by default. Clients may also support
        single-sided planes.

        \\sa UsdGeomGprim::GetDoubleSidedAttr()
        """
    )

    width: AttributeSpec[double] = AttributeSpec(double,
        doc="""The width of the plane, which aligns to the x-axis when \\em axis is
        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()
        """
    )

    length: AttributeSpec[double] = AttributeSpec(double,
        doc="""The length of the plane, which aligns to the y-axis when \\em axis is
        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()
        """
    )

    axis: AttributeSpec[Axis] = AttributeSpec(Axis,
        uniform=True,
        doc="""The axis along which the surface of the plane is aligned. When set
        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in
        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.

        \\sa UsdGeomGprim::GetAxisAttr().
        """
    )

    extent: AttributeSpec[List[float3]] = AttributeSpec(List[float3],
        value=[],
        doc="""Extent is re-defined on Plane only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr().
        """
    )
