from .prim import Prim
from .attribute import Attribute
from .dtypes import token
from .gf import float2
from .api_schema_base import APISchemaBase


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

    @classmethod
    def apply(cls, prim:Prim)->Prim:
        prim.metadata.apiSchemas.append(cls.__name__)
        prim.def_prop(Attribute(token, "name", value="custom", uniform=True, metadata={
            "doc": "The name of the color space defined on this prim."
        }))
        prim.def_prop(Attribute(float2, "redChroma", value=(1, 0), metadata={
            "doc": "Red chromaticity coordinates"
        }))
        prim.def_prop(Attribute(float2, "greenChroma", value=(0, 1), metadata={
            "doc": "Green chromaticity coordinates"
        }))
        prim.def_prop(Attribute(float2, "blueChroma", value=(0, 0), metadata={
            "doc": "Blue chromaticity coordinates"
        }))
        prim.def_prop(Attribute(float2, "whitePoint", value=(0.33333333, 0.33333333), metadata={
            "doc": "Whitepoint chromaticity coordinates"
        }))
        prim.def_prop(Attribute(float, "gamma", value=1.0, metadata={
            "doc": "Gamma value of the log section"
        }))
        prim.def_prop(Attribute(float, "linearBias", value=0.0, metadata={
            "doc": "Linear bias of the log section"
        }))
        return prim