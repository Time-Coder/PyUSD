from .physics import Physics
from .physics_joint import PhysicsJoint

class PhysicsPrismaticJoint(PhysicsJoint):
    """Predefined prismatic joint type (translation along prismatic 
    joint axis is permitted.)
    """

    @property
    def physics(self) -> Physics: ...

