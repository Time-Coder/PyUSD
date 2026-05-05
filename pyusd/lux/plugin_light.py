from ..geom.xformable import Xformable
from ..common import SchemaKind


class PluginLight(Xformable):
    """Light that provides properties that allow it to identify an 
    external SdrShadingNode definition, through UsdShadeNodeDefAPI, that can be 
    provided to render delegates without the need to provide a schema 
    definition for the light's type.
    
    \\see \\ref usdLux_PluginSchemas
    
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraIncludes": """
    #include "pxr/usd/usdShade/nodeDefAPI.h" """
        }
    }
