from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim

class Capsule_1(Gprim):
    """Defines a primitive capsule, i.e. a cylinder capped by two half
    spheres, with potentially different radii, centered at the origin, and whose
    spine is along the specified \\em axis.
    The spherical cap heights (sagitta) of the two endcaps are a function of
    the relative radii of the endcaps, such that cylinder tangent and sphere
    tangent are coincident and maintain C1 continuity.
    """

    @property
    def height(self)->AttributeSpec[double]:
        """The length of the capsule's spine along the specified
        \\em axis excluding the size of the two half spheres, i.e.
        the length of the cylinder portion of the capsule.
        If you author \\em height you must also author \\em extent.
        \\sa GetExtentAttr()"""

    @height.setter
    def height(self, value:double)->None: ...

    @property
    def radiusTop(self)->AttributeSpec[double]:
        """The radius of the capping sphere at the top of the capsule -
        i.e. the sphere in the direction of the positive \\em axis. If you
        author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusTop.setter
    def radiusTop(self, value:double)->None: ...

    @property
    def radiusBottom(self)->AttributeSpec[double]:
        """The radius of the capping sphere at the bottom of the capsule -
        i.e. the sphere located in the direction of the negative \\em axis. If
        you author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radiusBottom.setter
    def radiusBottom(self, value:double)->None: ...

    @property
    def axis(self)->AttributeSpec[Axis]:
        """The axis along which the spine of the capsule is aligned"""

    @axis.setter
    def axis(self, value:Axis)->None: ...

    @property
    def extent(self)->AttributeSpec[List[float3]]:
        """Extent is re-defined on Capsule only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""

    @extent.setter
    def extent(self, value:List[float3])->None: ...
