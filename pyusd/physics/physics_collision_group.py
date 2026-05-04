from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from typing import List
from ..dtypes import namespace
from ..dtypes import string
from ..common import SchemaKind

class PhysicsCollisionGroup(Typed):
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.mergeGroup = Attribute(string,
        doc="""If non-empty, any collision groups in a stage with a matching
        mergeGroup should be considered to refer to the same collection. Matching
        collision groups should behave as if there were a single group containing
        referenced colliders and filter groups from both collections.
        """,
        metadata={
            "customData": {
                "apiName": "mergeGroupName"
            },
            "displayName": "Merge With Groups"
        }
    )
    physics.invertFilteredGroups = Attribute(bool,
        doc="""Normally, the filter will disable collisions against the selected
        filter groups. However, if this option is set, the filter will disable
        collisions against all colliders except for those in the selected filter
        groups.
        """,
        metadata={
            "customData": {
                "apiName": "invertFilteredGroups"
            },
            "displayName": "Invert Filtered Groups"
        }
    )
    physics.filteredGroups = Relationship(
        doc="""References a list of PhysicsCollisionGroups with which 
        collisions should be ignored.
        """,
        metadata={
            "customData": {
                "apiName": "filteredGroups"
            },
            "displayName": "Filtered Groups"
        }
    )
