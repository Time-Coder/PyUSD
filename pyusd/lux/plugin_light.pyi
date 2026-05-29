from ..geom.xformable import Xformable

class PluginLight(Xformable):
    """Light that provides properties that allow it to identify an 
    external SdrShadingNode definition, through UsdShadeNodeDefAPI, that can be 
    provided to render delegates without the need to provide a schema 
    definition for the light's type.
    
    \\see \\ref usdLux_PluginSchemas
    
    """

