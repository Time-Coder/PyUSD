from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace, token
from .physics import Physics

class PhysicsDriveAPI(APISchemaBase):

    class Type(token):
        Force = "force"
        Acceleration = "acceleration"

    @property
    def physics(self) -> Physics: ...

