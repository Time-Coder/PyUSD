from .prim import Prim
from .attribute import Attribute
from .dtypes import token
from .gf import float2
from .api_schema_base import APISchemaBase
from .common import SchemaKind


class ColorSpaceDefinitionAPI(APISchemaBase):
    """UsdColorSpaceDefinitionAPI is an API schema for defining a custom
    color space. Custom color spaces become available for use on prims or for
    assignment to attributes via the colorSpace:name property on prims that have
    applied `UsdColorSpaceAPI`. Since color spaces inherit hierarchically, a
    custom color space defined on a prim will be available to all descendants of
    that prim, unless overridden by a more local color space definition bearing
    the same name. Locally redefining color spaces within the same layer could
    be confusing, so that practice is discouraged.

    The default color space values are equivalent to an identity transform, so
    applying this schema and invoking `UsdColorSpaceAPI::ComputeColorSpace()`
    on a prim resolving to a defaulted color definition will return a color
    space equivalent to the identity transform.
    """

    schema_kind = SchemaKind.MultipleApplyAPI
    
    meta = {
        "customData": {
            "apiSchemaType": "multipleApply",
            "propertyNamespacePrefix": "colorSpaceDefinition",
            "extraIncludes": """
#include "pxr/base/gf/colorSpace.h"
"""
        }
    }

    name: Attribute[token] = Attribute(token, value="custom", uniform=True, doc=
        "The name of the color space defined on this prim."
    )
    redChroma: Attribute[float2] = Attribute(float2, value=(1, 0), doc=
        "Red chromaticity coordinates"
    )
    greenChroma: Attribute[float2] = Attribute(float2, value=(0, 1), doc=
        "Green chromaticity coordinates"
    )
    blueChroma: Attribute[float2] = Attribute(float2, value=(0, 0), doc=
        "Blue chromaticity coordinates"
    )
    whitePoint: Attribute[float2] = Attribute(float2, value=(0.33333333, 0.33333333), doc=
        "Whitepoint chromaticity coordinates"
    )
    gamma: Attribute[float] = Attribute(float, value=1.0, doc=
        "Gamma value of the log section"
    )
    linearBias: Attribute[float] = Attribute(float, value=0.0, doc=
        "Linear bias of the log section"
    )
