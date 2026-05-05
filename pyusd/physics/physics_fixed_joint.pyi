from .physics_joint import PhysicsJoint
from .physics import Physics


class PhysicsFixedJoint(PhysicsJoint):
    """Predefined fixed joint type (All degrees of freedom are 
    removed.)
    """

