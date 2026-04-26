from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Cylinder_1(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis, with a pair of radii
    describing the size of the end points.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds."""
    
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

        self.create_prop(Attribute(double, "height", value=2, metadata={
            "doc": """The length of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(double, "radiusTop", value=1.0, metadata={
            "doc": """The radius of the top of the cylinder - i.e. the face located
        along the positive \\em axis. If you author \\em radiusTop you must also
        author \\em extent.

        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(double, "radiusBottom", value=1.0, metadata={
            "doc": """The radius of the bottom of the cylinder - i.e. the face
        point located along the negative \\em axis. If you author
        \\em radiusBottom you must also author \\em extent.

        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(token, "axis", value="Z", uniform=True, metadata={
            "allowedTokens": ["X", "Y", "Z"],
            "doc": """The axis along which the spine of the cylinder is aligned"""
        }))
        self.extent = [(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)]
        self.extent.metadata.update({
            "doc": """Extent is re-defined on Cylinder only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
        })
