from .boundable_light_base import BoundableLightBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class DiskLight(BoundableLightBase):
    """Light emitted from one side of a circular disk.
    The disk is centered in the XY plane and emits light along the -Z axis.
    """

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

