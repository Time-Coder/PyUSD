from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import namespace, token
from ..common import Axis
from .physics import Physics

class PhysicsSphericalJoint(Typed):
    @property
    def physics(self) -> Physics: ...

