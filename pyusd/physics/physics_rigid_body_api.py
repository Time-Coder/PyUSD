from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..gf import vector3f
from ..relationship import Relationship
from ..common import SchemaKind


class PhysicsRigidBodyAPI(APISchemaBase):
    """Applies physics body attributes to any UsdGeomXformable prim and
    marks that prim to be driven by a simulation. If a simulation is running
    it will update this prim's pose. All prims in the hierarchy below this 
    prim should move rigidly along with the body, except when the descendant
    prim has its own UsdPhysicsRigidBodyAPI (marking a separate rigid body
    subtree which moves independently of the parent rigid body)."""
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "RigidBodyAPI",
            "extraIncludes": """
                #include "pxr/base/gf/matrix3f.h"
                #include "pxr/base/gf/quatf.h" """
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.rigidBodyEnabled = Attribute(bool,
        value=True,
        doc="Determines if this PhysicsRigidBodyAPI is enabled.",
        metadata={
            "customData": {
                "apiName": "rigidBodyEnabled"
            },
            "displayName": "Rigid Body Enabled"
        }
    )
    physics.kinematicEnabled = Attribute(bool,
        value=False,
        doc=
        """Determines whether the body is kinematic or not. A kinematic 
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
    physics.startsAsleep = Attribute(bool,
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
    physics.velocity = Attribute(vector3f,
        doc=
        """Linear velocity in the same space as the node's xform. 
        Units: distance/second.
        """,
        metadata={
            "customData": {
                "apiName": "velocity"
            },
            "displayName": "Linear Velocity"
        }
    )
    physics.angularVelocity = Attribute(vector3f,
        doc=
        """Angular velocity in the same space as the node's xform. 
        Units: degrees/second.
        """,
        metadata={
            "customData": {
                "apiName": "angularVelocity"
            },
            "displayName": "Angular Velocity"
        }
    )

    simulationOwner: Relationship = Relationship(
        doc=
        """Single PhysicsScene that will simulate this body. By 
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
