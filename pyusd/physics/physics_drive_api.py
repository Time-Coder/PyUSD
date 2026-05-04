from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind

class PhysicsDriveAPI(APISchemaBase):
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    class Type(token):
        Force = "force"
        Acceleration = "acceleration"


    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.create_prop(Attribute(Type,
        name="type",
        uniform=True,
        doc="""Drive spring is for the acceleration at the joint (rather 
        than the force).
        """,
        metadata={
            "customData": {
                "apiName": "type"
            },
            "displayName": "Type"
        }
    ))
    physics.maxForce = Attribute(float,
        doc="""Maximum force that can be applied to drive. Units: 
        if linear drive: mass*DIST_UNITS/second/second
        if angular drive: mass*DIST_UNITS*DIST_UNITS/second/second
        inf means not limited. Must be non-negative.

        """,
        metadata={
            "customData": {
                "apiName": "maxForce"
            },
            "displayName": "Max Force"
        }
    )
    physics.targetPosition = Attribute(float,
        doc="""Target value for position. Units: 
        if linear drive: distance
        if angular drive: degrees.
        """,
        metadata={
            "customData": {
                "apiName": "targetPosition"
            },
            "displayName": "Target Position"
        }
    )
    physics.targetVelocity = Attribute(float,
        doc="""Target value for velocity. Units: 
        if linear drive: distance/second
        if angular drive: degrees/second.
        """,
        metadata={
            "customData": {
                "apiName": "targetVelocity"
            },
            "displayName": "Target Velocity"
        }
    )
    physics.damping = Attribute(float,
        doc="""Damping of the drive. Units: 
        if linear drive: mass/second
        If angular drive: mass*DIST_UNITS*DIST_UNITS/second/degrees.
        """,
        metadata={
            "customData": {
                "apiName": "damping"
            }
        }
    )
    physics.stiffness = Attribute(float,
        doc="""Stiffness of the drive. Units:
        if linear drive: mass/second/second
        if angular drive: mass*DIST_UNITS*DIST_UNITS/degrees/second/second.
        """,
        metadata={
            "customData": {
                "apiName": "stiffness"
            }
        }
    )
