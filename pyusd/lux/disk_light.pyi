from .boundable_light_base import BoundableLightBase
from .inputs import Inputs
from .light import Light

class DiskLight(BoundableLightBase):
    """Light emitted from one side of a circular disk.
    The disk is centered in the XY plane and emits light along the -Z axis.
    """

    @property
    def light(self) -> Light: ...

    @property
    def inputs(self) -> Inputs: ...

