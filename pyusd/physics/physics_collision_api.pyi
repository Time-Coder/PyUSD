from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace
from .physics import Physics

class PhysicsCollisionAPI(APISchemaBase):
    @property
    def physics(self) -> Physics: ...

