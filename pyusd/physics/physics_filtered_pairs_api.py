from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace
from ..common import SchemaKind


class PhysicsFilteredPairsAPI(APISchemaBase):
    """API to describe fine-grained filtering. If a collision between
    two objects occurs, this pair might be filtered if the pair is defined
    through this API. This API can be applied either to a body or collision
    or even articulation. The "filteredPairs" defines what objects it should 
    not collide against. Note that FilteredPairsAPI filtering has precedence 
    over CollisionGroup filtering.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "FilteredPairsAPI"
        }
    }

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
