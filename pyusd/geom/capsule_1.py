from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Capsule_1(Gprim):
    """Defines a primitive capsule, i.e. a cylinder capped by two half
    spheres, with potentially different radii, centered at the origin, and whose
    spine is along the specified \\em axis. 
    The spherical cap heights (sagitta) of the two endcaps are a function of 
    the relative radii of the endcaps, such that cylinder tangent and sphere 
    tangent are coincident and maintain C1 continuity."""
    
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

        self.create_prop(Attribute(double, "height", value=1.0, metadata={
            "doc": """The length of the capsule's spine along the specified
        \\em axis excluding the size of the two half spheres, i.e.
        the length of the cylinder portion of the capsule.
        If you author \\em height you must also author \\em extent.
        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(double, "radiusTop", value=0.5, metadata={
            "doc": """The radius of the capping sphere at the top of the capsule -
        i.e. the sphere in the direction of the positive \\em axis. If you
        author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(double, "radiusBottom", value=0.5, metadata={
            "doc": """The radius of the capping sphere at the bottom of the capsule -
        i.e. the sphere located in the direction of the negative \\em axis. If
        you author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(token, "axis", value="Z", uniform=True, metadata={
            "allowedTokens": ["X", "Y", "Z"],
            "doc": """The axis along which the spine of the capsule is aligned"""
        }))
        self.extent = [(-0.5, -0.5, -1.0), (0.5, 0.5, 1.0)]
        self.extent.metadata.update({
            "doc": """Extent is re-defined on Capsule only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
        })
