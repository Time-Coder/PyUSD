from .physics import Physics
from .physics_joint import PhysicsJoint

class PhysicsDistanceJoint(PhysicsJoint):
    """Predefined distance joint type (Distance between rigid bodies
    may be limited to given minimum or maximum distance.)
    """

    @property
    def physics(self) -> Physics: ...
