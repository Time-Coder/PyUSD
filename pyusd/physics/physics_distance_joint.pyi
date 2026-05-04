from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import namespace
from .physics import Physics

class PhysicsDistanceJoint(Typed):
    @property
    def physics(self) -> Physics: ...

