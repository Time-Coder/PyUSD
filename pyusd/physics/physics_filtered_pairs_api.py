from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from typing import List
from ..dtypes import namespace
from ..common import SchemaKind

class PhysicsFilteredPairsAPI(APISchemaBase):
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.filteredPairs = Relationship(
        doc="Relationship to objects that should be filtered.",
        metadata={
            "customData": {
                "apiName": "filteredPairs"
            },
            "displayName": "Filtered Pairs"
        }
    )
