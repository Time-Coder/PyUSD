from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim

class Cylinder_1(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis, with a pair of radii
    describing the size of the end points.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds.
    """

    @property
    def height(self)->AttributeSpec[double]:
        """The length of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @height.setter
    def height(self, value:double)->None: ...

    @property
    def radiusTop(self)->AttributeSpec[double]:
        """The radius of the top of the cylinder - i.e. the face located
        along the positive \\em axis. If you author \\em radiusTop you must also
        author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusTop.setter
    def radiusTop(self, value:double)->None: ...

    @property
    def radiusBottom(self)->AttributeSpec[double]:
        """The radius of the bottom of the cylinder - i.e. the face
        point located along the negative \\em axis. If you author
        \\em radiusBottom you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusBottom.setter
    def radiusBottom(self, value:double)->None: ...

    @property
    def axis(self)->AttributeSpec[Axis]:
        """The axis along which the spine of the cylinder is aligned"""

    @axis.setter
    def axis(self, value:Axis)->None: ...

    @property
    def extent(self)->AttributeSpec[List[float3]]:
        """Extent is re-defined on Cylinder only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""

    @extent.setter
    def extent(self, value:List[float3])->None: ...
