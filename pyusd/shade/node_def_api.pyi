from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, token
from .info import Info
from .outputs import Outputs


class NodeDefAPI(APISchemaBase):
    """UsdShadeNodeDefAPI is an API schema that provides attributes
    for a prim to select a corresponding Shader Node Definition ("Sdr Node"),
    as well as to look up a runtime entry for that shader node in the
    form of an SdrShaderNode.
    
    UsdShadeNodeDefAPI is intended to be a pre-applied API schema for any
    prim type that wants to refer to the SdrRegistry for further implementation
    details about the behavior of that prim.  The primary use in UsdShade
    itself is as UsdShadeShader, which is a basis for material shading networks
    (UsdShadeMaterial), but this is intended to be used in other domains
    that also use the Sdr node mechanism.
    
    This schema provides properties that allow a prim to identify an external
    node definition, either by a direct identifier key into the SdrRegistry
    (info:id), an asset to be parsed by a suitable SdrParserPlugin
    (info:sourceAsset), or an inline source code that must also be parsed
    (info:sourceCode); as well as a selector attribute to determine which
    specifier is active (info:implementationSource).
    
    """


    class ImplementationSource(token):
        Id = "id"
        SourceAsset = "sourceAsset"
        SourceCode = "sourceCode"

    @property
    def info(self) -> Info: ...

