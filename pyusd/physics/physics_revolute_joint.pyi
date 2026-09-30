from .physics import Physics
from .physics_joint import PhysicsJoint

class PhysicsRevoluteJoint(PhysicsJoint):
    """Predefined revolute joint type (rotation along revolute joint
    axis is permitted.)
    """

    @property
    def physics(self) -> Physics: ...
