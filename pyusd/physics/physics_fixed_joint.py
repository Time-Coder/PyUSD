from ..typed import Typed
from ..common import SchemaKind


class PhysicsFixedJoint(Typed):
    """Predefined fixed joint type (All degrees of freedom are 
    removed.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "FixedJoint"
        }
    }
