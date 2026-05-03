from ..boundable import Boundable
from ..common import SchemaKind


class BoundableLightBase(Boundable):
    """Base class for intrinsic lights that are boundable.

    The primary purpose of this class is to provide a direct API to the 
    functions provided by LightAPI for concrete derived light types.
    """
    schema_kind: SchemaKind = SchemaKind.AbstractTyped

    meta = {
        "customData": {
            "extraIncludes": "#include "pxr/usd/usdLux/lightAPI.h" ",
            "reflectedAPISchemas": "None"
        }
    }
