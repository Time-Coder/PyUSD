from .nonboundable_light_base import NonboundableLightBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class DistantLight(NonboundableLightBase):
    """Light emitted from a distant source along the -Z axis.
    Also known as a directional light."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        value="DistantLight",
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.angle = Attribute(float,
        value=0.53,
        doc=
        """Angular diameter of the light in degrees.
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
    inputs.intensity = Attribute(float,
        doc=
        """Scales the brightness of the light linearly.

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
