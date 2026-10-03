from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token
from .boundable_light_base import BoundableLightBase


class PortalLight(BoundableLightBase):
    """A rectangular portal in the local XY plane that guides sampling
    of a dome light.  Transmits light in the -Z direction.
    The rectangle is 1 unit in length.
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
        value="PortalLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    inputs.width = AttributeSpec(float,
        value=1,
        doc="Width of the portal rectangle in the local X axis.",
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
        doc="Height of the portal rectangle in the local Y axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Height",
            "customData": {
                "apiName": "height"
            }
        }
    )
