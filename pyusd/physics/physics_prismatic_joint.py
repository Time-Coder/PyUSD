from ..typed import Typed
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind
from ..common import Axis

class PhysicsPrismaticJoint(Typed):
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

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
