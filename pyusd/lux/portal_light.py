from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


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
    inputs.width = Attribute(float,
        doc="Width of the portal rectangle in the local X axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Width",
            "customData": {
                "apiName": "width"
            }
        }
    )
    inputs.height = Attribute(float,
        doc="Height of the portal rectangle in the local Y axis.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Height",
            "customData": {
                "apiName": "height"
            }
        }
    )
