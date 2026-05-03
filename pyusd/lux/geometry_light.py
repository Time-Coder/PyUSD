from .nonboundable_light_base import NonboundableLightBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..relationship import Relationship
from ..common import SchemaKind


class GeometryLight(NonboundableLightBase):
    """\\deprecated
    Light emitted outward from a geometric prim (UsdGeomGprim),
    which is typically a mesh."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        value="GeometryLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    geometry: Relationship = Relationship(doc="Relationship to the geometry to use as the light source.")
