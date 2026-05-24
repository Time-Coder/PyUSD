from .nonboundable_light_base import NonboundableLightBase
from ..attribute import Attribute
from ..dtypes import token
from .inputs import Inputs
from .light import Light


class DistantLight(NonboundableLightBase):
    """Light emitted from a distant source along the -Z axis.
    Also known as a directional light.
    """

    @property
    def light(self) -> Light: ...

    @property
    def inputs(self) -> Inputs: ...

