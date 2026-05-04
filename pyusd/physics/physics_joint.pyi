from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import quatf
from ..dtypes import namespace
from .physics import Physics

class PhysicsJoint(Typed):
    @property
    def physics(self) -> Physics: ...

