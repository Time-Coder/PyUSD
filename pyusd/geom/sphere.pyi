from typing import List

from ..attribute_spec import AttributeSpec
from ..dtypes import double
from ..gf import float3
from .gprim import Gprim

class Sphere(Gprim):
    """Defines a primitive sphere centered at the origin.

    The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
    they all pack into the same volume/bounds.
    """

    @property
    def radius(self)->AttributeSpec[double]:
        """Indicates the sphere's radius.  If you
        author \\em radius you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @radius.setter
    def radius(self, value:double)->None: ...

    @property
    def extent(self)->AttributeSpec[List[float3]]:
        """Extent is re-defined on Sphere only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""

    @extent.setter
    def extent(self, value:List[float3])->None: ...
