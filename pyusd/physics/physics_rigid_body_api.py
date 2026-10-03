from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace
from ..gf import vector3f
from ..relationship_spec import RelationshipSpec


class PhysicsRigidBodyAPI(APISchemaBase):
    """Applies physics body attributes to any UsdGeomXformable prim and
    marks that prim to be driven by a simulation. If a simulation is running
    it will update this prim's pose. All prims in the hierarchy below this
    prim should move rigidly along with the body, except when the descendant
    prim has its own UsdPhysicsRigidBodyAPI (marking a separate rigid body
    subtree which moves independently of the parent rigid body).
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "RigidBodyAPI",
            "extraIncludes": '''
    #include "pxr/base/gf/matrix3f.h"
    #include "pxr/base/gf/quatf.h" '''
        }
    }

    physics: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    physics.rigidBodyEnabled = AttributeSpec(bool,
        value=True,
        doc="Determines if this PhysicsRigidBodyAPI is enabled.",
        metadata={
            "customData": {
                "apiName": "rigidBodyEnabled"
            },
            "displayName": "Rigid Body Enabled"
        }
    )
    physics.kinematicEnabled = AttributeSpec(bool,
        value=False,
        doc="""Determines whether the body is kinematic or not. A kinematic
        body is a body that is moved through animated poses or through
        user defined poses. The simulation derives velocities for the
        kinematic body based on the external motion. When a continuous motion
        is not desired, this kinematic flag should be set to false.
        """,
        metadata={
            "customData": {
                "apiName": "kinematicEnabled"
            },
            "displayName": "Kinematic Enabled"
        }
    )
    physics.startsAsleep = AttributeSpec(bool,
        uniform=True,
        value=False,
        doc="Determines if the body is asleep when the simulation starts.",
        metadata={
            "customData": {
                "apiName": "startsAsleep"
            },
            "displayName": "Starts as Asleep"
        }
    )
    physics.velocity = AttributeSpec(vector3f,
        value=(0.0, 0.0, 0.0),
        doc="""Linear velocity in the same space as the node's xform.
        Units: distance/second.
        """,
        metadata={
            "customData": {
                "apiName": "velocity"
            },
            "displayName": "Linear Velocity"
        }
    )
    physics.angularVelocity = AttributeSpec(vector3f,
        value=(0.0, 0.0, 0.0),
        doc="""Angular velocity in the same space as the node's xform.
        Units: degrees/second.
        """,
        metadata={
            "customData": {
                "apiName": "angularVelocity"
            },
            "displayName": "Angular Velocity"
        }
    )
    physics.simulationOwner = RelationshipSpec(
        doc="""Single PhysicsScene that will simulate this body. By
        default this is the first PhysicsScene found in the stage using
        UsdStage::Traverse().
        """,
        metadata={
            "customData": {
                "apiName": "simulationOwner"
            },
            "displayName": "Simulation Owner"
        }
    )
