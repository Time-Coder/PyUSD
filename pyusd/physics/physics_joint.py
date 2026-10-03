from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace
from ..geom.imageable import Imageable
from ..gf import point3f, quatf
from ..relationship_spec import RelationshipSpec


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

    physics: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    physics.localPos0 = AttributeSpec(point3f,
        value=(0.0, 0.0, 0.0),
        doc="Relative position of the joint frame to body0's frame.",
        metadata={
            "customData": {
                "apiName": "localPos0"
            },
            "displayName": "Local Position 0"
        }
    )
    physics.localRot0 = AttributeSpec(quatf,
        value=(1.0, 0.0, 0.0, 0.0),
        doc="Relative orientation of the joint frame to body0's frame.",
        metadata={
            "customData": {
                "apiName": "localRot0"
            },
            "displayName": "Local Rotation 0"
        }
    )
    physics.localPos1 = AttributeSpec(point3f,
        value=(0.0, 0.0, 0.0),
        doc="Relative position of the joint frame to body1's frame.",
        metadata={
            "customData": {
                "apiName": "localPos1"
            },
            "displayName": "Local Position 1"
        }
    )
    physics.localRot1 = AttributeSpec(quatf,
        value=(1.0, 0.0, 0.0, 0.0),
        doc="Relative orientation of the joint frame to body1's frame.",
        metadata={
            "customData": {
                "apiName": "localRot1"
            },
            "displayName": "Local Rotation 1"
        }
    )
    physics.jointEnabled = AttributeSpec(bool,
        value=True,
        doc="Determines if the joint is enabled.",
        metadata={
            "customData": {
                "apiName": "jointEnabled"
            },
            "displayName": "Joint Enabled"
        }
    )
    physics.collisionEnabled = AttributeSpec(bool,
        value=False,
        doc="Determines if the jointed subtrees should collide or not.",
        metadata={
            "customData": {
                "apiName": "collisionEnabled"
            },
            "displayName": "Collision Enabled"
        }
    )
    physics.excludeFromArticulation = AttributeSpec(bool,
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
    physics.breakForce = AttributeSpec(float,
        value=float('inf'),
        doc="""Joint break force. If set, joint is to break when this force
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
    physics.breakTorque = AttributeSpec(float,
        value=float('inf'),
        doc="""Joint break torque. If set, joint is to break when this torque
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
    physics.body0 = RelationshipSpec(
        doc="Relationship to any UsdGeomXformable.",
        metadata={
            "customData": {
                "apiName": "body0"
            },
            "displayName": "Body 0"
        }
    )
    physics.body1 = RelationshipSpec(
        doc="Relationship to any UsdGeomXformable.",
        metadata={
            "customData": {
                "apiName": "body1"
            },
            "displayName": "Body 1"
        }
    )
