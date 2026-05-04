from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..gf import float3, point3f, quatf
from ..common import SchemaKind

class PhysicsMassAPI(APISchemaBase):
    """Defines explicit mass properties (mass, density, inertia etc.).        
    MassAPI can be applied to any object that has a PhysicsCollisionAPI or
    a PhysicsRigidBodyAPI.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "MassAPI"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.mass = Attribute(float,
        doc="""If non-zero, directly specifies the mass of the object.
        Note that any child prim can also have a mass when they apply massAPI.
        In this case, the precedence rule is 'parent mass overrides the
        child's'. This may come as counter-intuitive, but mass is a computed 
        quantity and in general not accumulative. For example, if a parent 
        has mass of 10, and one of two children has mass of 20, allowing 
        child's mass to override its parent results in a mass of -10 for the 
        other child. Note if mass is 0.0 it is ignored. Units: mass.

        """,
        metadata={
            "customData": {
                "apiName": "mass"
            },
            "displayName": "Mass"
        }
    )
    physics.density = Attribute(float,
        doc="""If non-zero, specifies the density of the object.
        In the context of rigid body physics, density indirectly results in 
        setting mass via (mass = density x volume of the object). How the 
        volume is computed is up to implementation of the physics system.
        It is generally computed from the collision approximation rather than
        the graphical mesh. In the case where both density and mass are 
        specified for the same object, mass has precedence over density. 
        Unlike mass, child's prim's density overrides parent prim's density 
        as it is accumulative. Note that density of a collisionAPI can be also
        alternatively set through a PhysicsMaterialAPI. The material density
        has the weakest precedence in density definition. Note if density is
        0.0 it is ignored. Units: mass/distance/distance/distance.
        """,
        metadata={
            "customData": {
                "apiName": "density"
            },
            "displayName": "Density"
        }
    )
    physics.centerOfMass = Attribute(point3f,
        doc="Center of mass in the prim's local space. Units: distance.",
        metadata={
            "customData": {
                "apiName": "centerOfMass"
            },
            "displayName": "Center of Mass"
        }
    )
    physics.diagonalInertia = Attribute(float3,
        doc="""If non-zero, specifies diagonalized inertia tensor along the 
        principal axes. Note if diagonalInertial is (0.0, 0.0, 0.0) it is 
        ignored. Units: mass*distance*distance.
        """,
        metadata={
            "customData": {
                "apiName": "diagonalInertia"
            },
            "displayName": "Diagonal Inertia"
        }
    )
    physics.principalAxes = Attribute(quatf,
        doc="""Orientation of the inertia tensor's principal axes in the 
        prim's local space.
        """,
        metadata={
            "customData": {
                "apiName": "principalAxes"
            },
            "displayName": "Principal Axes"
        }
    )
