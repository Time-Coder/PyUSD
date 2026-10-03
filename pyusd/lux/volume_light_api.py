from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token


class VolumeLightAPI(APISchemaBase):
    """This is the preferred API schema to apply to
    \\ref UsdVolVolume "Volume" type prims when adding light behaviors to a
    volume. At its base, this API schema has the built-in behavior of applying
    LightAPI to the volume and overriding the default materialSyncMode to allow
    the emission/glow of the bound material to affect the color of the light.
    But, it additionally serves as a hook for plugins to attach additional
    properties to "volume lights" through the creation of API schemas which are
    authored to auto-apply to VolumeLightAPI.
    \\see \\ref Usd_AutoAppliedAPISchemas

    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "prepend apiSchemas": ["LightAPI"]
    }

    light: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    light.shaderId = AttributeSpec(token,
        uniform=True,
        value="VolumeLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )
    light.materialSyncMode = AttributeSpec(token,
        uniform=True,
        value="materialGlowTintsLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )
