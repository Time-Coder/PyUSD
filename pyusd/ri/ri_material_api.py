from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class RiMaterialAPI(APISchemaBase):
    """
    \\deprecated Materials should use UsdShadeMaterial instead.
    This schema will be removed in a future release.

    This API provides outputs that connect a material prim to prman 
    shaders and RIS objects."""
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "MaterialAPI",
            "extraIncludes": """
                #include "pxr/usd/usdShade/input.h"
                #include "pxr/usd/usdShade/output.h"
                #include "pxr/usd/usdShade/material.h"
                """
        }
    }

    outputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    outputs.ri.surface = Attribute(token,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "surface"
            }
        }
    )
    outputs.ri.displacement = Attribute(token,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "displacement"
            }
        }
    )
    outputs.ri.volume = Attribute(token,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "volume"
            }
        }
    )
