from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from typing import List
from ..dtypes import namespace
from ..common import SchemaKind

class PhysicsCollisionAPI(APISchemaBase):
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.collisionEnabled = Attribute(bool,
        doc="Determines if the PhysicsCollisionAPI is enabled.",
        metadata={
            "customData": {
                "apiName": "collisionEnabled"
            },
            "displayName": "Collision Enabled"
        }
    )
    physics.simulationOwner = Relationship(
        doc="""Single PhysicsScene that will simulate this collider. 
        By default this object belongs to the first PhysicsScene.
        Note that if a RigidBodyAPI in the hierarchy above has a different
        simulationOwner then it has a precedence over this relationship.
        """,
        metadata={
            "customData": {
                "apiName": "simulationOwner"
            },
            "displayName": "Simulation Owner"
        }
    )
