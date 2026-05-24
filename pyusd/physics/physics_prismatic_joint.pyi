from .physics_joint import PhysicsJoint
from ..attribute import Attribute
from ..dtypes import token
from ..common import Axis
from .physics import Physics


class PhysicsPrismaticJoint(PhysicsJoint):
    """Predefined prismatic joint type (translation along prismatic 
    joint axis is permitted.)
    """

    @property
    def physics(self) -> Physics: ...

