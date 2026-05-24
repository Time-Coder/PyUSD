from .nonboundable_light_base import NonboundableLightBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from .light import Light


class GeometryLight(NonboundableLightBase):
    """\\deprecated
    Light emitted outward from a geometric prim (UsdGeomGprim),
    which is typically a mesh.
    """

    @property
    def light(self) -> Light: ...

    @property
    def geometry(self)->Relationship:
        """Relationship to the geometry to use as the light source."""

    @geometry.setter
    def geometry(self, value:Relationship)->None: ...

