from ..api_schema_base import APISchemaBase
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class NonboundableLightBase(APISchemaBase):
    """Base class for intrinsic lights that are not boundable.
    
    The primary purpose of this class is to provide a direct API to the 
    functions provided by LightAPI for concrete derived light types.
    
    """

