from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import asset, token
from ..common import SchemaKind


class RectLight(BoundableLightBase):
    """Light emitted from one side of a rectangle.
    The rectangle is centered in the XY plane and emits light along the -Z axis.
    The rectangle is 1 unit in length in the X and Y axis.  In the default 
    position, a texture file's min coordinates should be at (+X, +Y) and 
    max coordinates at (-X, -Y)."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": "None"
            }
        }
    }

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        value="RectLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.width = Attribute(float,
        doc="Width of the rectangle, in the local X axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Width",
            "customData": {
                "apiName": "width"
            }
        }
    )
    inputs.height = Attribute(float,
        doc="Height of the rectangle, in the local Y axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Height",
            "customData": {
                "apiName": "height"
            }
        }
    )
    inputs.texture.file = Attribute(asset,
        doc="A color texture to use on the rectangle.",
        metadata={
            "displayGroup": "Basic",
            "displayName": "Color Map",
            "customData": {
                "apiName": "textureFile"
            }
        }
    )
