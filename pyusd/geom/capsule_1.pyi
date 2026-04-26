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
    def radiusTop(self)->Attribute[double]:
        """The radius of the capping sphere at the top of the capsule -
        i.e. the sphere in the direction of the positive \\em axis. If you
        author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusTop.setter
    def radiusTop(self, value:float)->None: ...

    @property
    def radiusBottom(self)->Attribute[double]:
        """The radius of the capping sphere at the bottom of the capsule -
        i.e. the sphere located in the direction of the negative \\em axis. If
        you author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusBottom.setter
    def radiusBottom(self, value:float)->None: ...

    @property
    def axis(self)->Attribute[token]:
        """The axis along which the spine of the capsule is aligned"""

    @axis.setter
    def axis(self, value:token)->None: ...
