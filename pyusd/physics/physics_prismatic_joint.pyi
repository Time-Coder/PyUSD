from ..typed import Typed
from ..dtypes import namespace, token
from ..common import Axis
from .physics import Physics


class PhysicsPrismaticJoint(Typed):
    """Predefined prismatic joint type (translation along prismatic 
    joint axis is permitted.)
    """

    @property
    def physics(self) -> Physics: ...

