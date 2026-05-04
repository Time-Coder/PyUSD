from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..common import SchemaKind

class PhysicsLimitAPI(APISchemaBase):
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.low = Attribute(float,
        doc="""Lower limit. Units: degrees or distance depending on trans or
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
        doc="""Upper limit. Units: degrees or distance depending on trans or 
        rot axis applied to. inf means not limited in positive direction.
        """,
        metadata={
            "customData": {
                "apiName": "high"
            },
            "displayName": "High Limit"
        }
    )
