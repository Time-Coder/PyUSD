from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace
from ..relationship_spec import RelationshipSpec


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

    physics: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    physics.filteredPairs = RelationshipSpec(
        doc="Relationship to objects that should be filtered.",
        metadata={
            "customData": {
                "apiName": "filteredPairs"
            },
            "displayName": "Filtered Pairs"
        }
    )
