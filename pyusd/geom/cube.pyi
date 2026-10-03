from typing import List

from ..attribute_spec import AttributeSpec
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim

class Cube(Gprim):
    """Defines a primitive rectilinear cube centered at the origin.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds.
    """

    @property
    def size(self)->AttributeSpec[double]:
        """Indicates the length of each edge of the cube.  If you
        author \\em size you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @size.setter
    def size(self, value:double)->None: ...

    @property
    def extent(self)->AttributeSpec[List[float3]]:
        """Extent is re-defined on Cube only to provide a fallback value.
        \\sa UsdGeomGprim::GetExtentAttr()."""

    @extent.setter
    def extent(self, value:List[float3])->None: ...
