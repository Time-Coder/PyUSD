from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import namespace
from ..common import SchemaKind


class PhysicsDistanceJoint(Typed):
    """Predefined distance joint type (Distance between rigid bodies
    may be limited to given minimum or maximum distance.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "DistanceJoint"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.minDistance = Attribute(float,
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
    physics.maxDistance = Attribute(float,
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
