from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token
from .boundable_light_base import BoundableLightBase


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

    light: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    light.shaderId = AttributeSpec(token,
        uniform=True,
        value="SphereLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    inputs.radius = AttributeSpec(float,
        value=0.5,
        doc="Radius of the sphere.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Radius",
            "customData": {
                "apiName": "radius"
            }
        }
    )

    treatAsPoint: AttributeSpec[bool] = AttributeSpec(bool,
        value=False,
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
