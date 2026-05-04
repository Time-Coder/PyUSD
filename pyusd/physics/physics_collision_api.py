from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace
from ..common import SchemaKind

class PhysicsCollisionAPI(APISchemaBase):
    """Applies collision attributes to a UsdGeomXformable prim. If a 
    simulation is running, this geometry will collide with other geometries that 
    have PhysicsCollisionAPI applied. If any prim in the parent hierarchy has
    the RigidBodyAPI applied, the collider is considered a part of the closest
    ancestor body. If there is no body in the parent hierarchy, this collider
    is considered to be static.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "CollisionAPI"
        }
    }

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
