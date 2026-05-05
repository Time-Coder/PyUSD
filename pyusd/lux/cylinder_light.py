from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


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
    inputs.length = Attribute(float,
        doc="Length of the cylinder, in the local X axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Length",
            "customData": {
                "apiName": "length"
            }
        }
    )
    inputs.radius = Attribute(float,
        doc="Radius of the cylinder.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Radius",
            "customData": {
                "apiName": "radius"
            }
        }
    )

    treatAsLine = Attribute(bool,
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
