from .physics_joint import PhysicsJoint
from ..dtypes import namespace, token
from ..common import Axis
from .physics import Physics


class PhysicsRevoluteJoint(PhysicsJoint):
    """Predefined revolute joint type (rotation along revolute joint
    axis is permitted.)
    """

    @property
    def physics(self) -> Physics: ...

