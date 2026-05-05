from .boundable_light_base import BoundableLightBase
from ..dtypes import asset, namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class RectLight(BoundableLightBase):
    """Light emitted from one side of a rectangle.
    The rectangle is centered in the XY plane and emits light along the -Z axis.
    The rectangle is 1 unit in length in the X and Y axis.  In the default 
    position, a texture file's min coordinates should be at (+X, +Y) and 
    max coordinates at (-X, -Y).
    """

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

