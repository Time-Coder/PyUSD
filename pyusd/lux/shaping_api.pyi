from ..api_schema_base import APISchemaBase
from ..dtypes import asset, namespace
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class ShapingAPI(APISchemaBase):
    "Controls for shaping a light's emission."

    @property
    def inputs(self) -> Inputs: ...

