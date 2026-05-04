from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from .physics import Physics

class PhysicsFilteredPairsAPI(APISchemaBase):
    @property
    def physics(self) -> Physics: ...

