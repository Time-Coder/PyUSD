from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..gf import float3, quatf
from ..dtypes import namespace
from .physics import Physics

class PhysicsMassAPI(APISchemaBase):
    @property
    def physics(self) -> Physics: ...

