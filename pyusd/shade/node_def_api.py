from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


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

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "extraIncludes": """
    #include "pxr/usd/sdr/declare.h"
    #include "pxr/usd/sdr/shaderNode.h"
        """,
            "schemaTokens": {
                "universalSourceType": {"value": "", "doc": """Possible value for the "sourceType" parameter 
                    in \\ref UsdShadeNodeDefAPI_ImplementationSource API. Represents 
                    the universal or fallback source type.
                    """},
                "sdrMetadata": {"doc": """Dictionary valued metadata key authored on
                    Shader prims with implementationSource value of sourceAsset or 
                    sourceCode to pass along metadata to the shader parser or 
                    compiler. It is also used to author metadata on shader 
                    properties in a UsdShade-based shader definition file.
                    """},
                "subIdentifier": {"doc": """This identifier is used in conjunction with a
                    specific source asset to indicate a particular definition within
                    the source asset, if the source asset specifies more than one
                    shader node definition.
                    """}
            }
        }
    }

    class ImplementationSource(token):
        Id = "id"
        SourceAsset = "sourceAsset"
        SourceCode = "sourceCode"


    info: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    info.implementationSource = Attribute(ImplementationSource,
        uniform=True,
        doc="""Specifies the attribute that should be consulted to get the 
        shader's implementation or its source code.

        * If set to "id", the "info:id" attribute's value is used to 
        determine the shader source from the shader registry.
        * If set to "sourceAsset", the resolved value of the "info:sourceAsset" 
        attribute corresponding to the desired implementation (or source-type)
        is used to locate the shader source.  A source asset file may also
        specify multiple shader definitions, so there is an optional attribute
        "info:sourceAsset:subIdentifier" whose value should be used to indicate
        a particular shader definition from a source asset file.
        * If set to "sourceCode", the value of "info:sourceCode" attribute 
        corresponding to the desired implementation (or source type) is used as 
        the shader source.

        """,
        metadata={
            "customData": {
                "apiName": "implementationSource"
            }
        }
    )
    info.id = Attribute(token,
        uniform=True,
        doc="""The id is an identifier for the type or purpose of the 
        shader. E.g.: Texture or FractalFloat.
        The use of this id will depend on the render context: some will turn it
        into an actual shader path, some will use it to generate shader source 
        code dynamically.

        \\sa SetShaderId()

        """,
        metadata={
            "customData": {
                "apiName": "id"
            }
        }
    )
