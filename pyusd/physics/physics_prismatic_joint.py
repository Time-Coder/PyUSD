from ..attribute import Attribute
from ..common import Axis, SchemaKind
from ..dtypes import namespace
from .physics_joint import PhysicsJoint


class PhysicsPrismaticJoint(PhysicsJoint):
    """Predefined prismatic joint type (translation along prismatic 
    joint axis is permitted.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "PrismaticJoint"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.axis = Attribute(Axis,
        uniform=True,
        doc="Joint axis.",
        metadata={
            "customData": {
                "apiName": "axis"
            },
            "displayName": "Axis"
        }
    )
    physics.lowerLimit = Attribute(float,
        doc="""Lower limit. Units: distance. -inf means not limited in 
        negative direction.
        """,
        metadata={
            "customData": {
                "apiName": "lowerLimit"
            },
            "displayName": "Lower Limit"
        }
    )
    physics.upperLimit = Attribute(float,
        doc="""Upper limit. Units: distance. inf means not limited in 
        positive direction.
        """,
        metadata={
            "customData": {
                "apiName": "upperLimit"
            },
            "displayName": "Upper Limit"
        }
    )
