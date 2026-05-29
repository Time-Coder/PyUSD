from ..api_schema_base import APISchemaBase
from .inputs import Inputs

class ShapingAPI(APISchemaBase):
    "Controls for shaping a light's emission."

    @property
    def inputs(self) -> Inputs: ...

