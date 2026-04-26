from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double


class Sphere(Gprim):
    """Defines a primitive sphere centered at the origin.
    
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

        self.create_prop(Attribute(double, "radius", value=1.0, metadata={
            "doc": """Indicates the sphere's radius.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
        }))

        self.extent = [(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)]
        self.extent.metadata.update({
            "doc": """Extent is re-defined on Sphere only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
        })