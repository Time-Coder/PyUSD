from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token
from ..common import SchemaKind


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

    def __init__(self, name:str="")->None:
        Gprim.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraPlugInfo": {
                    "implementsComputeExtent": True
                }
            }
        })

        self.doubleSided = True
        self.doubleSided.metadata.update({
            "doc": """Planes are double-sided by default. Clients may also support
        single-sided planes.

        \\sa UsdGeomGprim::GetDoubleSidedAttr()"""
        })
        self.create_prop(Attribute(double, "width", value=2.0, metadata={
            "doc": """The width of the plane, which aligns to the x-axis when \\em axis is
        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width 
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""
        }))
        self.create_prop(Attribute(double, "length", value=2.0, metadata={
            "doc": """The length of the plane, which aligns to the y-axis when \\em axis is
        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length 
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""
        }))
        self.create_prop(Attribute(token, "axis", value="Z", uniform=True, metadata={
            "allowedTokens": ["X", "Y", "Z"],
            "doc": """The axis along which the surface of the plane is aligned. When set
        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in 
        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.

        \\sa UsdGeomGprim::GetAxisAttr()."""
        }))
        self.extent = [(-1.0, -1.0, 0.0), (1.0, 1.0, 0.0)]
        self.extent.metadata.update({
            "doc": """Extent is re-defined on Plane only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
        })
