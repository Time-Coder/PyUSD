from .nonboundable_light_base import NonboundableLightBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class DistantLight(NonboundableLightBase):
    """Light emitted from a distant source along the -Z axis.
    Also known as a directional light.
    """

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

