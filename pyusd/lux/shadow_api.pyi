from ..api_schema_base import APISchemaBase
from ..dtypes import namespace
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class ShadowAPI(APISchemaBase):
    """Controls to refine a light's shadow behavior.  These are
    non-physical controls that are valuable for visual lighting work.
    """

    @property
    def inputs(self) -> Inputs: ...

