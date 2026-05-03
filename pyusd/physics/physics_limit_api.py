from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..common import SchemaKind


class PhysicsLimitAPI(APISchemaBase):
    """The PhysicsLimitAPI can be applied to a PhysicsJoint and will
    restrict the movement along an axis. PhysicsLimitAPI is a multipleApply 
    schema: The PhysicsJoint can be restricted along "transX", "transY", 
    "transZ", "rotX", "rotY", "rotZ", "distance". Setting these as a 
    multipleApply schema TfToken name will define the degree of freedom the
    PhysicsLimitAPI is applied to. Note that if the low limit is higher than 
    the high limit, motion along this axis is considered locked."""
    schema_kind: SchemaKind = SchemaKind.MultipleApplyAPI

    meta = {
        "customData": {
            "className": "LimitAPI",
            "apiSchemaType": "multipleApply",
            "propertyNamespacePrefix": "limit"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.low = Attribute(float,
        value=float('-inf'),
        doc=
        """Lower limit. Units: degrees or distance depending on trans or
        rot axis applied to. -inf means not limited in negative direction.
        """,
        metadata={
            "customData": {
                "apiName": "low"
            },
            "displayName": "Low Limit"
        }
    )
    physics.high = Attribute(float,
        value=float('inf'),
        doc=
        """Upper limit. Units: degrees or distance depending on trans or 
        rot axis applied to. inf means not limited in positive direction.
        """,
        metadata={
            "customData": {
                "apiName": "high"
            },
            "displayName": "High Limit"
        }
    )
