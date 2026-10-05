from ..attribute_spec import AttributeSpec
from .boundable_light_base import BoundableLightBase
from .inputs import Inputs
from .light import Light

class CylinderLight(BoundableLightBase):
    """Light emitted outward from a cylinder.
    The cylinder is centered at the origin and has its major axis on the X axis.
    The cylinder does not emit light from the flat end-caps.

    """

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

    @property
    def treatAsLine(self)->AttributeSpec[bool]:
        """A hint that this light can be treated as a 'line'
        light (effectively, a zero-radius cylinder) by renderers that
        benefit from non-area lighting. Renderers that only support
        area lights can disregard this."""

    @treatAsLine.setter
    def treatAsLine(self, value:bool)->None: ...
