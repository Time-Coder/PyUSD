from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token


class RiMaterialAPI(APISchemaBase):
    """
    \\deprecated Materials should use UsdShadeMaterial instead.
    This schema will be removed in a future release.

    This API provides outputs that connect a material prim to prman
    shaders and RIS objects.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "MaterialAPI",
            "extraIncludes": '''
    #include "pxr/usd/usdShade/input.h"
    #include "pxr/usd/usdShade/output.h"
    #include "pxr/usd/usdShade/material.h"
    '''
        }
    }

    outputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    outputs.ri.surface = AttributeSpec(token,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "surface"
            }
        }
    )
    outputs.ri.displacement = AttributeSpec(token,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "displacement"
            }
        }
    )
    outputs.ri.volume = AttributeSpec(token,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "volume"
            }
        }
    )
