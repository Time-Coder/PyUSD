from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class BoundableLightBase(APISchemaBase):
    """Base class for intrinsic lights that are boundable.
    
    The primary purpose of this class is to provide a direct API to the 
    functions provided by LightAPI for concrete derived light types.
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "extraIncludes": "#include "pxr/usd/usdLux/lightAPI.h" ",
            "reflectedAPISchemas": None
        }
    }
