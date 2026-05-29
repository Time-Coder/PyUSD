from .light_filter import LightFilter

class PluginLightFilter(LightFilter):
    """Light filter that provides properties that allow it to identify an 
    external SdrShadingNode definition, through UsdShadeNodeDefAPI, that can be 
    provided to render delegates without the need to provide a schema 
    definition for the light filter's type.
    
    \\see \\ref usdLux_PluginSchemas
    
    """

