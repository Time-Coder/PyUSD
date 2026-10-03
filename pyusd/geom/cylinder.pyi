from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim

class Cylinder(Gprim):
    """Defines a primitive cylinder with closed ends, centered at the
    origin, whose spine is along the specified \\em axis.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds.
    """

    @property
    def height(self)->AttributeSpec[double]:
        """The size of the cylinder's spine along the specified
        \\em axis.  If you author \\em height you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @height.setter
    def height(self, value:double)->None: ...

    @property
    def radius(self)->AttributeSpec[double]:
        """The radius of the cylinder. If you author \\em radius
        you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radius.setter
    def radius(self, value:double)->None: ...

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
