from ..attribute_spec import AttributeSpec
from .boundable_light_base import BoundableLightBase
from .inputs import Inputs
from .light import Light

class SphereLight(BoundableLightBase):
    "Light emitted outward from a sphere."

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

    @property
    def treatAsPoint(self)->AttributeSpec[bool]:
        """A hint that this light can be treated as a 'point'
        light (effectively, a zero-radius sphere) by renderers that
        benefit from non-area lighting. Renderers that only support
        area lights can disregard this."""

    @treatAsPoint.setter
    def treatAsPoint(self, value:bool)->None: ...
