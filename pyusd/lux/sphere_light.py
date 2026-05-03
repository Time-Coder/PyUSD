from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class SphereLight(BoundableLightBase):
    """Light emitted outward from a sphere."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": "None"
            }
        }
    }

    treatAsPoint: Attribute[bool] = Attribute(bool,
        value=False,
        doc=
        """A hint that this light can be treated as a 'point'
        light (effectively, a zero-radius sphere) by renderers that
        benefit from non-area lighting. Renderers that only support
        area lights can disregard this.
        """,
        metadata={
            "displayGroup": "Advanced",
            "displayName": "Treat As Point"
        }
    )

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        value="SphereLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.radius = Attribute(float,
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
