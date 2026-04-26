from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token


class Plane(Gprim):
    "Defines a primitive plane, centered at the origin, and is defined by\n    a cardinal axis, width, and length. The plane is double-sided by default.\n\n    The axis of width and length are perpendicular to the plane's \\em axis:\n\n    axis  | width  | length\n    ----- | ------ | -------\n    X     | z-axis | y-axis\n    Y     | x-axis | z-axis\n    Z     | x-axis | y-axis\n\n    "
    def __init__(self, name:str="")->None: ...

    @property
    def width(self)->Attribute[double]:
        "The width of the plane, which aligns to the x-axis when \\em axis is\n        'Z' or 'Y', or to the z-axis when \\em axis is 'X'.  If you author \\em width \n        you must also author \\em extent.\n\n        \\sa UsdGeomGprim::GetExtentAttr()"


    @width.setter
    def width(self, value:float)->None: ...

    @property
    def length(self)->Attribute[double]:
        "The length of the plane, which aligns to the y-axis when \\em axis is\n        'Z' or 'X', or to the z-axis when \\em axis is 'Y'.  If you author \\em length \n        you must also author \\em extent.\n\n        \\sa UsdGeomGprim::GetExtentAttr()"


    @length.setter
    def length(self, value:float)->None: ...

    @property
    def axis(self)->Attribute[token]:
        "The axis along which the surface of the plane is aligned. When set\n        to 'Z' the plane is in the xy-plane; when \\em axis is 'X' the plane is in \n        the yz-plane, and when \\em axis is 'Y' the plane is in the xz-plane.\n\n        \\sa UsdGeomGprim::GetAxisAttr()."


    @axis.setter
    def axis(self, value:token)->None: ...
