from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token
from .boundable_light_base import BoundableLightBase


class CylinderLight(BoundableLightBase):
    """Light emitted outward from a cylinder.
    The cylinder is centered at the origin and has its major axis on the X axis.
    The cylinder does not emit light from the flat end-caps.

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
        value="CylinderLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    inputs.length = AttributeSpec(float,
        value=1,
        doc="Length of the cylinder, in the local X axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Length",
            "customData": {
                "apiName": "length"
            }
        }
    )
    inputs.radius = AttributeSpec(float,
        value=0.5,
        doc="Radius of the cylinder.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Radius",
            "customData": {
                "apiName": "radius"
            }
        }
    )

    treatAsLine: AttributeSpec[bool] = AttributeSpec(bool,
        value=False,
        doc="""A hint that this light can be treated as a 'line'
        light (effectively, a zero-radius cylinder) by renderers that
        benefit from non-area lighting. Renderers that only support
        area lights can disregard this.
        """,
        metadata={
            "displayGroup": "Advanced",
            "displayName": "Treat As Line"
        }
    )
