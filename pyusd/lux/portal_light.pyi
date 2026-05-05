from .boundable_light_base import BoundableLightBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class PortalLight(BoundableLightBase):
    """A rectangular portal in the local XY plane that guides sampling
    of a dome light.  Transmits light in the -Z direction.
    The rectangle is 1 unit in length.
    """

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

