from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import namespace
from .physics import Physics

class PhysicsDistanceJoint(Typed):
    """Predefined distance joint type (Distance between rigid bodies
    may be limited to given minimum or maximum distance.)
    """

    @property
    def physics(self) -> Physics: ...

