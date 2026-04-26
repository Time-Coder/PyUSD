from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Cone(Gprim):
    """Defines a primitive cone, centered at the origin, whose spine
    is along the specified \\em axis, with the apex of the cone pointing
    in the direction of the positive axis.
    
    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds."""
        
    def __init__(self, name:str="")->None: ...

    @property
    def height(self)->Attribute[double]:
        """The length of the cone's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.
        
        \\sa GetExtentAttr()"""

    @height.setter
    def height(self, value:float)->None: ...

    @property
    def radius(self)->Attribute[double]:
        """The radius of the cone.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""

    @radius.setter
    def radius(self, value:float)->None: ...

    @property
    def axis(self)->Attribute[token]:
        """The axis along which the spine of the cone is aligned"""

    @axis.setter
    def axis(self, value:token)->None: ...
