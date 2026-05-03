from .physics_joint import PhysicsJoint
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..common import SchemaKind


class PhysicsDistanceJoint(PhysicsJoint):
    """Predefined distance joint type (Distance between rigid bodies
    may be limited to given minimum or maximum distance.)"""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "DistanceJoint"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.minDistance = Attribute(float,
        value=-1.0,
        doc=
        """Minimum distance. If attribute is negative, the joint is not 
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
        value=-1.0,
        doc=
        """Maximum distance. If attribute is negative, the joint is not 
        limited. Units: distance.
        """,
        metadata={
            "customData": {
                "apiName": "maxDistance"
            },
            "displayName": "Maximum Distance"
        }
    )
