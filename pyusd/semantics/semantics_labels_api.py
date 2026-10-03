from typing import List

from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import token


class SemanticsLabelsAPI(APISchemaBase):
    """Application of labels for a prim for a taxonomy specified by the
    schema's instance name.

    See `UsdSemanticsLabelsQuery` for more information about computations and
    inheritance of semantics.
    """

    schema_kind: SchemaKind = SchemaKind.MultipleApplyAPI

    meta = {
        "customData": {
            "className": "LabelsAPI",
            "apiSchemaType": "multipleApply",
            "propertyNamespacePrefix": "semantics:labels"
        }
    }

    __INSTANCE_NAME__: AttributeSpec[List[token]] = AttributeSpec(List[token],
        value=[],
        doc="Array of labels specified directly at this prim.",
        metadata={
            "customData": {
                "apiName": "Labels"
            }
        }
    )
