from ..attribute_spec import AttributeSpec
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

    physics: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    physics.axis = AttributeSpec(Axis,
        uniform=True,
        value="X",
        doc="Joint axis.",
        metadata={
            "customData": {
                "apiName": "axis"
            },
            "displayName": "Axis"
        }
    )
    physics.lowerLimit = AttributeSpec(float,
        value=float('-inf'),
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
    physics.upperLimit = AttributeSpec(float,
        value=float('inf'),
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
