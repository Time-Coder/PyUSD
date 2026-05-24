from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..gf import float3, point3f, quatf
from .physics import Physics


class PhysicsMassAPI(APISchemaBase):
    """Defines explicit mass properties (mass, density, inertia etc.).        
    MassAPI can be applied to any object that has a PhysicsCollisionAPI or
    a PhysicsRigidBodyAPI.
    """

    @property
    def physics(self) -> Physics: ...

