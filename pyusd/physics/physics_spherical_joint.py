from .physics_joint import PhysicsJoint
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind
from ..common import Axis


class PhysicsSphericalJoint(PhysicsJoint):
    """Predefined spherical joint type (Removes linear degrees of 
    freedom, cone limit may restrict the motion in a given range.) It allows
    two limit values, which when equal create a circular, else an elliptic 
    cone limit around the limit axis."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "SphericalJoint"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.axis = Attribute(Axis,
        uniform=True,
        value="X",
        doc="Cone limit axis.",
        metadata={
            "customData": {
                "apiName": "axis"
            },
            "displayName": "Axis"
        }
    )
    physics.coneAngle0Limit = Attribute(float,
        value=-1.0,
        doc=
        """Cone limit from the primary joint axis in the local0 frame 
        toward the next axis. (Next axis of X is Y, and of Z is X.) A 
        negative value means not limited. Units: degrees.
        """,
        metadata={
            "customData": {
                "apiName": "coneAngle0Limit"
            },
            "displayName": "Cone Angle0 Limit"
        }
    )
    physics.coneAngle1Limit = Attribute(float,
        value=-1.0,
        doc=
        """Cone limit from the primary joint axis in the local0 frame 
        toward the second to next axis. A negative value means not limited. 
        Units: degrees.
        """,
        metadata={
            "customData": {
                "apiName": "coneAngle1Limit"
            },
            "displayName": "Cone Angle1 Limit"
        }
    )
