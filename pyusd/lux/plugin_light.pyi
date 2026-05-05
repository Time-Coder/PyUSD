from ..geom.xformable import Xformable
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class PluginLight(Xformable):
    """Light that provides properties that allow it to identify an 
    external SdrShadingNode definition, through UsdShadeNodeDefAPI, that can be 
    provided to render delegates without the need to provide a schema 
    definition for the light's type.
    
    \\see \\ref usdLux_PluginSchemas
    
    """

