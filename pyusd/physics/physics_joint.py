from pyusd.geom.imageable import Imageable
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..gf import point3f, quatf
from ..relationship import Relationship
from ..common import SchemaKind


class PhysicsJoint(Imageable):
    """A joint constrains the movement of rigid bodies. Joint can be 
    created between two rigid bodies or between one rigid body and world.
    By default joint primitive defines a D6 joint where all degrees of 
    freedom are free. Three linear and three angular degrees of freedom.
    Note that default behavior is to disable collision between jointed bodies.
    """
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Joint"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.localPos0 = Attribute(point3f,
        doc="Relative position of the joint frame to body0's frame.",
        metadata={
            "customData": {
                "apiName": "localPos0"
            },
            "displayName": "Local Position 0"
        }
    )
    physics.localRot0 = Attribute(quatf,
        doc="Relative orientation of the joint frame to body0's frame.",
        metadata={
            "customData": {
                "apiName": "localRot0"
            },
            "displayName": "Local Rotation 0"
        }
    )
    physics.localPos1 = Attribute(point3f,
        doc="Relative position of the joint frame to body1's frame.",
        metadata={
            "customData": {
                "apiName": "localPos1"
            },
            "displayName": "Local Position 1"
        }
    )
    physics.localRot1 = Attribute(quatf,
        doc="Relative orientation of the joint frame to body1's frame.",
        metadata={
            "customData": {
                "apiName": "localRot1"
            },
            "displayName": "Local Rotation 1"
        }
    )
    physics.jointEnabled = Attribute(bool,
        value=True,
        doc="Determines if the joint is enabled.",
        metadata={
            "customData": {
                "apiName": "jointEnabled"
            },
            "displayName": "Joint Enabled"
        }
    )
    physics.collisionEnabled = Attribute(bool,
        value=False,
        doc="Determines if the jointed subtrees should collide or not.",
        metadata={
            "customData": {
                "apiName": "collisionEnabled"
            },
            "displayName": "Collision Enabled"
        }
    )
    physics.excludeFromArticulation = Attribute(bool,
        uniform=True,
        value=False,
        doc="Determines if the joint can be included in an Articulation.",
        metadata={
            "customData": {
                "apiName": "excludeFromArticulation"
            },
            "displayName": "Exclude From Articulation"
        }
    )
    physics.breakForce = Attribute(float,
        value=float('inf'),
        doc=
        """Joint break force. If set, joint is to break when this force
        limit is reached. (Used for linear DOFs.) 
        Units: mass * distance / second / second
        """,
        metadata={
            "customData": {
                "apiName": "breakForce"
            },
            "displayName": "Break Force"
        }
    )
    physics.breakTorque = Attribute(float,
        value=float('inf'),
        doc=
        """Joint break torque. If set, joint is to break when this torque
        limit is reached. (Used for angular DOFs.) 
        Units: mass * distance * distance / second / second
        """,
        metadata={
            "customData": {
                "apiName": "breakTorque"
            },
            "displayName": "Break Torque"
        }
    )

    body0: Relationship = Relationship(
        doc="Relationship to any UsdGeomXformable.",
        metadata={
            "customData": {
                "apiName": "body0"
            },
            "displayName": "Body 0"
        }
    )

    body1: Relationship = Relationship(
        doc="Relationship to any UsdGeomXformable.",
        metadata={
            "customData": {
                "apiName": "body1"
            },
            "displayName": "Body 1"
        }
    )
