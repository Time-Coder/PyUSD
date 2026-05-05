from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..gf import color3f
from ..common import SchemaKind


class ShadowAPI(APISchemaBase):
    """Controls to refine a light's shadow behavior.  These are
    non-physical controls that are valuable for visual lighting work.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "extraIncludes": """
    #include "pxr/usd/usdShade/input.h"
    #include "pxr/usd/usdShade/output.h" """
        }
    }

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.shadow.enable = Attribute(bool,
        doc="Enables shadows to be cast by this light.",
        metadata={
            "displayGroup": "Shadows",
            "displayName": "Enable Shadows",
            "customData": {
                "apiName": "shadow:enable"
            }
        }
    )
    inputs.shadow.color = Attribute(color3f,
        doc="""The color of shadows cast by the light.  This is a
        non-physical control.  The default is to cast black shadows.
        """,
        metadata={
            "displayGroup": "Shadows",
            "displayName": "Shadow Color",
            "customData": {
                "apiName": "shadow:color"
            }
        }
    )
    inputs.shadow.distance = Attribute(float,
        doc="""The maximum distance shadows are cast. The distance is
        measured as the distance between the point on the surface and the 
        occluder.
        The default value (-1) indicates no limit.

        """,
        metadata={
            "displayGroup": "Shadows",
            "displayName": "Shadow Max Distance",
            "customData": {
                "apiName": "shadow:distance"
            }
        }
    )
    inputs.shadow.falloff = Attribute(float,
        doc="""The size of the shadow falloff zone within the shadow max 
        distance, which can be used to hide the hard cut-off for shadows seen 
        stretching past the max distance. The falloff zone is the area that 
        fades from full shadowing at the beginning of the falloff zone to no 
        shadowing at the max distance from the occluder. The falloff zone 
        distance cannot exceed the shadow max distance. A falloff value equal 
        to or less than zero (with -1 as the default) indicates no falloff. 

        """,
        metadata={
            "displayGroup": "Shadows",
            "displayName": "Shadow Falloff",
            "customData": {
                "apiName": "shadow:falloff"
            }
        }
    )
    inputs.shadow.falloffGamma = Attribute(float,
        doc="""A gamma (i.e., exponential) control over shadow strength
        with linear distance within the falloff zone. This controls the rate
        of the falloff.
        This requires the use of shadowDistance and shadowFalloff.
        """,
        metadata={
            "displayGroup": "Shadows",
            "displayName": "Shadow Falloff Gamma",
            "customData": {
                "apiName": "shadow:falloffGamma"
            }
        }
    )
