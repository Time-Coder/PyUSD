from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Cylinder(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the 
    origin, whose spine is along the specified \\em axis.
    
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

        self.create_prop(Attribute(double, "height", value=2.0, metadata={
            "doc": """The size of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
        }))
        self.create_prop(Attribute(double, "radius", value=1.0, metadata={
            "doc": """The radius of the cylinder. If you author \\em radius
        you must also author \\em extent.
        
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
