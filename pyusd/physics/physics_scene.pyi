from ..typed import Typed
from ..attribute import Attribute
from ..gf import vector3f
from ..dtypes import namespace
from .physics import Physics

class PhysicsScene(Typed):
    "General physics simulation properties, required for simulation."

    @property
    def physics(self) -> Physics: ...

