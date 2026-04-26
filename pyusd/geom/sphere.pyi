from .mesh import Mesh
from ..attribute import Attribute
from ..dtypes import double


class Sphere(Mesh):
    """Defines a primitive sphere centered at the origin.
    
    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds."""
    
    def __init__(self, name:str="")->None: ...

    @property
    def radius(self) -> Attribute[double]:
        """Indicates the sphere's radius.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""

    @radius.setter
    def radius(self, value:float) -> None: ...