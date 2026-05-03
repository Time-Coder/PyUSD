from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class Shader(Typed):
    """Base class for all USD shaders. Shaders are the building blocks
    of shading networks. While UsdShadeShader objects are not target specific,
    each renderer or application target may derive its own renderer-specific 
    shader object types from this base, if needed.
    
    Objects of this class generally represent a single shading object, whether
    it exists in the target renderer or not. For example, a texture, a fractal,
    or a mix node.

    The UsdShadeNodeDefAPI provides attributes to uniquely identify the
    type of this node.  The id resolution into a renderable shader target
    type of this node.  The id resolution into a renderable shader target
    is deferred to the consuming application.

    The purpose of representing them in Usd is two-fold:
    \\li To represent, via "connections" the topology of the shading network
    that must be reconstructed in the renderer. Facilities for authoring and 
    manipulating connections are encapsulated in the API schema 
    UsdShadeConnectableAPI.
    \\li To present a (partial or full) interface of typed input parameters 
    whose values can be set and overridden in Usd, to be provided later at 
    render-time as parameter values to the actual render shader objects. Shader 
    input parameters are encapsulated in the property schema UsdShadeInput.
    """
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "providesUsdShadeConnectableAPIBehavior": "None"
            },
            "extraIncludes": """'''
                #include "pxr/usd/usdShade/input.h"
                #include "pxr/usd/usdShade/output.h"
                #include "pxr/usd/usdShade/tokens.h"
                #include "pxr/usd/sdr/declare.h"
                #include "pxr/usd/sdr/shaderNode.h"'''"""
        }
    }
