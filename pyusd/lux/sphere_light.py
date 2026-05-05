from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class SphereLight(BoundableLightBase):
    "Light emitted outward from a sphere."

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": None
            }
        }
    }

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.radius = Attribute(float,
        doc="Radius of the sphere.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Radius",
            "customData": {
                "apiName": "radius"
            }
        }
    )

    treatAsPoint = Attribute(bool,
        doc="""A hint that this light can be treated as a 'point'
        light (effectively, a zero-radius sphere) by renderers that
        benefit from non-area lighting. Renderers that only support
        area lights can disregard this.
        """,
        metadata={
            "displayGroup": "Advanced",
            "displayName": "Treat As Point"
        }
    )
