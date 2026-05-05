from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class VolumeLightAPI(APISchemaBase):
    """This is the preferred API schema to apply to 
    \\ref UsdVolVolume "Volume" type prims when adding light behaviors to a 
    volume. At its base, this API schema has the built-in behavior of applying 
    LightAPI to the volume and overriding the default materialSyncMode to allow 
    the emission/glow of the bound material to affect the color of the light. 
    But, it additionally serves as a hook for plugins to attach additional 
    properties to "volume lights" through the creation of API schemas which are 
    authored to auto-apply to VolumeLightAPI.
    \\see \\ref Usd_AutoAppliedAPISchemas
    
    """

    @property
    def light(self) -> Light: ...

