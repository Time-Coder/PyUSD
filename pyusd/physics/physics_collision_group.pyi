from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace, string
from .physics import Physics

class PhysicsCollisionGroup(Typed):
    @property
    def physics(self) -> Physics: ...

