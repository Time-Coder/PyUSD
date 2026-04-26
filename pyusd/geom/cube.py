from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double


class Cube(Gprim):
    """Defines a primitive rectilinear cube centered at the origin.
    
    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds."""

    def __init__(self, name:str="")->None:
        Gprim.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraPlugInfo": {
                    "implementsComputeExtent": True
                }
            }
        })

        self.def_prop(Attribute(double, "size", value=2.0, metadata={
            "doc": """Indicates the length of each edge of the cube.  If you
        author \\em size you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
        }))
        
        self.extent = [(-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)]
        self.extent.metadata.update({
            "doc": """Extent is re-defined on Cube only to provide a fallback value.
        \\sa UsdGeomGprim::GetExtentAttr()."""
        })