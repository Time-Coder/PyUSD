from typing import List

from ..attribute_spec import AttributeSpec
from ..common import Axis
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim

class Plane(Gprim):
    """Defines a primitive plane, centered at the origin, and is defined by
    a cardinal axis, width, and length. The plane is double-sided by default.

    The axis of width and length are perpendicular to the plane's \\em axis:

    axis  | width  | length
    ----- | ------ | -------
    X     | z-axis | y-axis
    Y     | x-axis | z-axis
    Z     | x-axis | y-axis


    """

    @property
    def doubleSided(self)->AttributeSpec[bool]:
        """Planes are double-sided by default. Clients may also support
        single-sided planes.

        \\sa UsdGeomGprim::GetDoubleSidedAttr()"""

    @doubleSided.setter
    def doubleSided(self, value:bool)->None: ...

    @property
    def width(self)->AttributeSpec[double]:
        """The width of the plane, which aligns to the x-axis when \\em axis is
        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""

    @width.setter
    def width(self, value:double)->None: ...

    @property
    def length(self)->AttributeSpec[double]:
        """The length of the plane, which aligns to the y-axis when \\em axis is
        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""

    @length.setter
    def length(self, value:double)->None: ...

    @property
    def axis(self)->AttributeSpec[Axis]:
        """The axis along which the surface of the plane is aligned. When set
        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in
        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.

        \\sa UsdGeomGprim::GetAxisAttr()."""

    @axis.setter
    def axis(self, value:Axis)->None: ...

    @property
    def extent(self)->AttributeSpec[List[float3]]:
        """Extent is re-defined on Plane only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""

    @extent.setter
    def extent(self, value:List[float3])->None: ...
