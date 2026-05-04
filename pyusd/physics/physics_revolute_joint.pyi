from ..typed import Typed
from ..dtypes import namespace, token
from ..common import Axis
from .physics import Physics


class PhysicsRevoluteJoint(Typed):
    """Predefined revolute joint type (rotation along revolute joint
    axis is permitted.)
    """

    @property
    def physics(self) -> Physics: ...

