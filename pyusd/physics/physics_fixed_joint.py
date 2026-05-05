from .physics_joint import PhysicsJoint
from ..common import SchemaKind


class PhysicsFixedJoint(PhysicsJoint):
    """Predefined fixed joint type (All degrees of freedom are 
    removed.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "FixedJoint"
        }
    }
