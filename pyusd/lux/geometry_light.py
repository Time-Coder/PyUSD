from ..attribute import Attribute
from ..common import SchemaKind
from ..dtypes import namespace, token
from ..relationship import Relationship
from .nonboundable_light_base import NonboundableLightBase


class GeometryLight(NonboundableLightBase):
    """\\deprecated
    Light emitted outward from a geometric prim (UsdGeomGprim),
    which is typically a mesh.
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    geometry = Relationship(doc="Relationship to the geometry to use as the light source.")
