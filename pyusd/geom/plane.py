from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Plane(Gprim):
    "Defines a primitive plane, centered at the origin, and is defined by\n    a cardinal axis, width, and length. The plane is double-sided by default.\n\n    The axis of width and length are perpendicular to the plane's \\em axis:\n\n    axis  | width  | length\n    ----- | ------ | -------\n    X     | z-axis | y-axis\n    Y     | x-axis | z-axis\n    Z     | x-axis | y-axis\n\n    "
    abstract: bool = False

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
        self.create_prop(Attribute(double, "width", value=2.0, metadata={
            "doc": """The size of the plane along its width axis."""
        }))
        self.create_prop(Attribute(double, "length", value=2.0, metadata={
            "doc": """The size of the plane along its length axis."""
        }))
        self.create_prop(Attribute(token, "axis", value="Z", uniform=True, metadata={
            "allowedTokens": ["X", "Y", "Z"],
            "doc": """The axis perpendicular to the plane."""
        }))
        self.extent = [(-1.0, -1.0, 0.0), (1.0, 1.0, 0.0)]
        self.extent.metadata.update({
            "doc": """Extent is re-defined on Plane only to provide a fallback
        value."""
        })
        # DOCSYNC-BEGIN Plane
        self.doubleSided.metadata.update({"doc": 'Planes are double-sided by default. Clients may also support\n        single-sided planes.\n\n        \\sa UsdGeomGprim::GetDoubleSidedAttr()'})
        self.width.metadata.update({"doc": "The width of the plane, which aligns to the x-axis when \\em axis is\n        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width \n        you must also author \\em extent.\n\n        \\sa UsdGeomGprim::GetExtentAttr()"})
        self.length.metadata.update({"doc": "The length of the plane, which aligns to the y-axis when \\em axis is\n        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length \n        you must also author \\em extent.\n\n        \\sa UsdGeomGprim::GetExtentAttr()"})
        self.axis.metadata.update({"doc": "The axis along which the surface of the plane is aligned. When set\n        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in \n        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.\n\n        \\sa UsdGeomGprim::GetAxisAttr()."})
        self.extent.metadata.update({"doc": 'Extent is re-defined on Plane only to provide a fallback\n        value. \\sa UsdGeomGprim::GetExtentAttr().'})
        # DOCSYNC-END Plane
