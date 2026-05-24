from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from ..dtypes import token
from .inputs import Inputs
from .light import Light


class PortalLight(BoundableLightBase):
    """A rectangular portal in the local XY plane that guides sampling
    of a dome light.  Transmits light in the -Z direction.
    The rectangle is 1 unit in length.
    """

    @property
    def light(self) -> Light: ...

    @property
    def inputs(self) -> Inputs: ...

