from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..gf import color3f
from ..dtypes import asset
from .inputs import Inputs


class ShapingAPI(APISchemaBase):
    "Controls for shaping a light's emission."

    @property
    def inputs(self) -> Inputs: ...

