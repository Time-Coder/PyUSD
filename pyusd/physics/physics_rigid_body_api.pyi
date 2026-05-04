from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import vector3f
from ..dtypes import namespace
from .physics import Physics

class PhysicsRigidBodyAPI(APISchemaBase):
    @property
    def physics(self) -> Physics: ...

