from ..common import SchemaKind
from .physics_joint import PhysicsJoint


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
