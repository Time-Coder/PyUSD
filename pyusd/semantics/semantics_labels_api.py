from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..common import SchemaKind


class SemanticsLabelsAPI(APISchemaBase):
    """Application of labels for a prim for a taxonomy specified by the
    schema's instance name.
    
    See `UsdSemanticsLabelsQuery` for more information about computations and
    inheritance of semantics.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "LabelsAPI",
            "apiSchemaType": "multipleApply",
            "propertyNamespacePrefix": "semantics:labels"
        }
    }

    __INSTANCE_NAME__ = Attribute(List[token],
        doc="Array of labels specified directly at this prim.",
        metadata={
            "customData": {
                "apiName": "Labels"
            }
        }
    )
