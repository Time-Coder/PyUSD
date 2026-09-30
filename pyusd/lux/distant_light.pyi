from .inputs import Inputs
from .light import Light
from .nonboundable_light_base import NonboundableLightBase

class DistantLight(NonboundableLightBase):
    """Light emitted from a distant source along the -Z axis.
    Also known as a directional light.
    """

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...
