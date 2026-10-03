from ..attribute_spec import AttributeSpec
from ..common import Axis, SchemaKind
from ..dtypes import namespace
from .physics_joint import PhysicsJoint


class PhysicsRevoluteJoint(PhysicsJoint):
    """Predefined revolute joint type (rotation along revolute joint
    axis is permitted.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "RevoluteJoint"
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
        doc="""Lower limit. Units: degrees. -inf means not limited in
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
        doc="""Upper limit. Units: degrees. inf means not limited in
        positive direction.
        """,
        metadata={
            "customData": {
                "apiName": "upperLimit"
            },
            "displayName": "Upper Limit"
        }
    )
