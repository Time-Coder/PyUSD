from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Cylinder_1(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis, with a pair of radii
    describing the size of the end points.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds."""
    
    def __init__(self, name:str="")->None: ...

    @property
    def height(self)->Attribute[double]:
        """The length of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @height.setter
    def height(self, value:float)->None: ...

    @property
    def radiusTop(self)->Attribute[double]:
        """The radius of the top of the cylinder - i.e. the face located
        along the positive \\em axis. If you author \\em radiusTop you must also
        author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusTop.setter
    def radiusTop(self, value:float)->None: ...

    @property
    def radiusBottom(self)->Attribute[double]:
        """The radius of the bottom of the cylinder - i.e. the face
        point located along the negative \\em axis. If you author
        \\em radiusBottom you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusBottom.setter
    def radiusBottom(self, value:float)->None: ...

    @property
    def axis(self)->Attribute[token]:
        """The axis along which the spine of the cylinder is aligned"""

    @axis.setter
    def axis(self, value:token)->None: ...
