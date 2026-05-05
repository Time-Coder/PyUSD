from .nonboundable_light_base import NonboundableLightBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


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

