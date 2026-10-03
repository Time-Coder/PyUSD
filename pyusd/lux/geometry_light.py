from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token
from ..relationship_spec import RelationshipSpec
from .nonboundable_light_base import NonboundableLightBase


class GeometryLight(NonboundableLightBase):
    """\\deprecated
    Light emitted outward from a geometric prim (UsdGeomGprim),
    which is typically a mesh.
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    light: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    light.shaderId = AttributeSpec(token,
        uniform=True,
        value="GeometryLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    geometry = RelationshipSpec(doc="Relationship to the geometry to use as the light source.")
