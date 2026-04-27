from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


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
    
    def __init__(self, name:str="")->None: ...

    @property
    def width(self)->Attribute[double]:
        """The width of the plane, which aligns to the x-axis when \\em axis is
        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width 
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""

    @width.setter
    def width(self, value:float)->None: ...

    @property
    def length(self)->Attribute[double]:
        """The length of the plane, which aligns to the y-axis when \\em axis is
        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length 
        you must also author \\em extent.

        \\sa UsdGeomGprim::GetExtentAttr()"""

    @length.setter
    def length(self, value:float)->None: ...

    @property
    def axis(self)->Attribute[token]:
        """The axis along which the surface of the plane is aligned. When set
        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in 
        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.

        \\sa UsdGeomGprim::GetAxisAttr()."""

    @axis.setter
    def axis(self, value:token)->None: ...
