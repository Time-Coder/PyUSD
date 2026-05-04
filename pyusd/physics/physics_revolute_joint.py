from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind
from ..common import Axis

class PhysicsRevoluteJoint(Typed):
    """Predefined revolute joint type (rotation along revolute joint
    axis is permitted.)
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "RevoluteJoint"
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
    physics.upperLimit = Attribute(float,
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
