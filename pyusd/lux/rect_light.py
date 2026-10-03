from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import asset, namespace, token
from .boundable_light_base import BoundableLightBase


class RectLight(BoundableLightBase):
    """Light emitted from one side of a rectangle.
    The rectangle is centered in the XY plane and emits light along the -Z axis.
    The rectangle is 1 unit in length in the X and Y axis.  In the default
    position, a texture file's min coordinates should be at (+X, +Y) and
    max coordinates at (-X, -Y).
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": None
            }
        }
    }

    light: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    light.shaderId = AttributeSpec(token,
        uniform=True,
        value="RectLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    inputs.width = AttributeSpec(float,
        value=1,
        doc="Width of the rectangle, in the local X axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Width",
            "customData": {
                "apiName": "width"
            }
        }
    )
    inputs.height = AttributeSpec(float,
        value=1,
        doc="Height of the rectangle, in the local Y axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Height",
            "customData": {
                "apiName": "height"
            }
        }
    )
    inputs.texture.file = AttributeSpec(asset,
        doc="A color texture to use on the rectangle.",
        metadata={
            "displayGroup": "Basic",
            "displayName": "Color Map",
            "customData": {
                "apiName": "textureFile"
            }
        }
    )
