from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from .physics import Physics

class PhysicsLimitAPI(APISchemaBase):
    @property
    def physics(self) -> Physics: ...

