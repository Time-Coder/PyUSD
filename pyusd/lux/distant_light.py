from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token
from .nonboundable_light_base import NonboundableLightBase


class DistantLight(NonboundableLightBase):
    """Light emitted from a distant source along the -Z axis.
    Also known as a directional light.
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    light: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    light.shaderId = AttributeSpec(token,
        uniform=True,
        value="DistantLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    inputs.angle = AttributeSpec(float,
        value=0.53,
        doc="""Angular diameter of the light in degrees.
        As an example, the Sun is approximately 0.53 degrees as seen from Earth.
        Higher values broaden the light and therefore soften shadow edges.

        This value is assumed to be in the range `0 <= angle < 360`, and will
        be clipped to this range. Note that this implies that we can have a
        distant light emitting from more than a hemispherical area of light
        if angle > 180. While this is valid, it is possible that for large
        angles a DomeLight may provide better performance. If angle is 0, the
        DistantLight represents a perfectly parallel light source.

        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Angle Extent",
            "customData": {
                "apiName": "angle"
            }
        }
    )
    inputs.intensity = AttributeSpec(float,
        value=50000,
        doc="""Scales the brightness of the light linearly.

        Intensity is overridden on DistantLight from LightAPI so that we can
        supply a high default intensity to approximate the Sun.

        """,
        metadata={
            "customData": {
                "apiName": "intensity",
                "apiSchemaOverride": True
            }
        }
    )
