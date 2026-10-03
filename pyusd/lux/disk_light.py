from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token
from .boundable_light_base import BoundableLightBase


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

    light: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    light.shaderId = AttributeSpec(token,
        uniform=True,
        value="DiskLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    inputs.radius = AttributeSpec(float,
        value=0.5,
        doc="Radius of the disk.",
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Radius",
            "customData": {
                "apiName": "radius"
            }
        }
    )
