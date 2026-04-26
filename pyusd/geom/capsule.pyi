from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Capsule(Gprim):
    """Defines a primitive capsule, i.e. a cylinder capped by two half
    spheres, centered at the origin, whose spine is along the specified
    \\em axis.
    The spherical cap heights (sagitta) of the two endcaps are a function of 
    the relative radii of the endcaps, such that cylinder tangent and sphere 
    tangent are coincident and maintain C1 continuity."""
        
    def __init__(self, name:str="")->None: ...

    @property
    def height(self)->Attribute[double]:
        """The length of the capsule's spine along the specified
        \\em axis excluding the size of the two half spheres, i.e.
        the length of the cylinder portion of the capsule.
        If you author \\em height you must also author \\em extent.
        \\sa GetExtentAttr()"""

    @height.setter
    def height(self, value:float)->None: ...

    @property
    def radius(self)->Attribute[double]:
        """The radius of the capsule.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""

    @radius.setter
    def radius(self, value:float)->None: ...

    @property
    def axis(self)->Attribute[token]:
        """The axis along which the spine of the capsule is aligned"""

    @axis.setter
    def axis(self, value:token)->None: ...
