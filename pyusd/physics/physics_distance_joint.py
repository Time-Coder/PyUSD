from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace
from .physics_joint import PhysicsJoint


class PhysicsDistanceJoint(PhysicsJoint):
    """Predefined distance joint type (Distance between rigid bodies
    may be limited to given minimum or maximum distance.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "DistanceJoint"
        }
    }

    physics: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    physics.minDistance = AttributeSpec(float,
        value=-1.0,
        doc="""Minimum distance. If attribute is negative, the joint is not
        limited. Units: distance.
        """,
        metadata={
            "customData": {
                "apiName": "minDistance"
            },
            "displayName": "Minimum Distance"
        }
    )
    physics.maxDistance = AttributeSpec(float,
        value=-1.0,
        doc="""Maximum distance. If attribute is negative, the joint is not
        limited. Units: distance.
        """,
        metadata={
            "customData": {
                "apiName": "maxDistance"
            },
            "displayName": "Maximum Distance"
        }
    )
