from .boundable_light_base import BoundableLightBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class DiskLight(BoundableLightBase):
    """Light emitted from one side of a circular disk.
    The disk is centered in the XY plane and emits light along the -Z axis.
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
    inputs.radius = Attribute(float,
        doc="Radius of the disk.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Radius",
            "customData": {
                "apiName": "radius"
            }
        }
    )
