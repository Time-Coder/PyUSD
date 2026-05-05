from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..gf import color3f
from ..dtypes import asset
from ..common import SchemaKind


class ShapingAPI(APISchemaBase):
    "Controls for shaping a light's emission."

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "extraIncludes": """
    #include "pxr/usd/usdShade/input.h"
    #include "pxr/usd/usdShade/output.h" """
        }
    }

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.shaping.focus = Attribute(float,
        doc="""A control to shape the spread of light.  Higher focus
        values pull light towards the center and narrow the spread.

        This is implemented as a multiplication with the absolute value of the
        dot product between the light's primary axis and the emission
        direction, raised to the power `focus`.  See `inputs:shaping:focusTint`
        for the complete formula, but if we assume a default `focusTint` of
        pure black, then that formula simplifies to:

        <center><b>
            focusFactor = ｜emissionDirection • lightAxis｜<sup>focus</sup>

                    L<sub>Color</sub> = focusFactor ⋅ L<sub>Color</sub>
        </b></center>

        Values < 0 are ignored.

        Note that the absolute value in the formula above means that sphere and 
        cylinder lights will emit "behind" the light as well as in front. If it 
        is desired that the light emits forward only, this can be achieved by setting
        the `inputs:shaping:coneAngle` to 90 degrees or less.

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "Emission Focus",
            "customData": {
                "apiName": "shaping:focus"
            }
        }
    )
    inputs.shaping.focusTint = Attribute(color3f,
        doc="""Off-axis color tint.  This tints the emission in the
        falloff region.  The default tint is black.

        This is implemented as a linear interpolation between `focusTint` and
        white, by the factor computed from the focus attribute, in other words:

        <center><b>
            focusFactor = ｜emissionDirection • lightAxis｜<sup>focus</sup>

                focusColor = lerp(focusFactor, focusTint, [1, 1, 1])

                L<sub>Color</sub> =
                    componentwiseMultiply(focusColor, L<sub>Color</sub>)
        </b></center>

        Note that this implies that a focusTint of pure white will disable
        focus.

        Note that the absolute value in the formula above means that sphere and 
        cylinder lights will emit "behind" the light as well as in front. If it 
        is desired that the light emits forward only, this can be achieved by setting
        the `inputs:shaping:coneAngle` to 90 degrees or less.

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "Emission Focus Tint",
            "customData": {
                "apiName": "shaping:focusTint"
            }
        }
    )
    inputs.shaping.cone.angle = Attribute(float,
        doc="""Angular limit off the primary axis to restrict the light
        spread, in degrees.

        Light emissions at angles off the primary axis greater than this are
        guaranteed to be zero, i.e.:


        <center><b>
                    𝛳<sub>offAxis</sub> = acos(lightAxis • emissionDir)

                    𝛳<sub>cutoff</sub> = toRadians(coneAngle)


                    𝛳<sub>offAxis</sub> > 𝛳<sub>cutoff</sub>
                            ⟹ L<sub>Scalar</sub> = 0

        </b></center>

        For angles < coneAngle, see the documentation for `shaping:cone:softness`.
        However, at the default of coneSoftness = 0, the luminance is
        unaltered if emissionOffAxisAngle <= coneAngle, so the coneAngle
        functions as a hard binary "off" toggle for all angles > coneAngle.

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "Cone Angle",
            "customData": {
                "apiName": "shaping:cone:angle"
            }
        }
    )
    inputs.shaping.cone.softness = Attribute(float,
        doc="""Controls the cutoff softness for cone angle.

        At the default of coneSoftness = 0, the luminance is unaltered if 
        emissionOffAxisAngle <= coneAngle, and 0 if
        emissionOffAxisAngle > coneAngle, so in this situation the coneAngle
        functions as a hard binary "off" toggle for all angles > coneAngle.

        For coneSoftness in the range (0, 1], it defines the proportion of the
        non-cutoff angles over which the luminance is smoothly interpolated from
        0 to 1. Mathematically:

        <center><b>
                𝛳<sub>offAxis</sub> = acos(lightAxis • emissionDir)

                    𝛳<sub>cutoff</sub> = toRadians(coneAngle)

          𝛳<sub>smoothStart</sub> = lerp(coneSoftness, 𝛳<sub>cutoff</sub>, 0)

            L<sub>Scalar</sub> = L<sub>Scalar</sub> ⋅
                    (1 - smoothStep(𝛳<sub>offAxis</sub>,
                                    𝛳<sub>smoothStart</sub>,
                                    𝛳<sub>cutoff</sub>)
        </b></center>

        Values outside of the [0, 1] range are clamped to the range.

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "Cone Softness",
            "customData": {
                "apiName": "shaping:cone:softness"
            }
        }
    )
    inputs.shaping.ies.file = Attribute(asset,
        doc="""An IES (Illumination Engineering Society) light
        profile describing the angular distribution of light.

        For full details on the .ies file format, see the full specification,
        ANSI/IES LM-63-19:

        https://store.ies.org/product/lm-63-19-approved-method-ies-standard-file-format-for-the-electronic-transfer-of-photometric-data-and-related-information/

        The luminous intensity values in the IES profile are sampled using
        the emission direction in the light's local space (after a possible
        transformation by a non-zero shaping:ies:angleScale, see below). The
        sampled value is then potentially normalized by the overall power of the
        profile if shaping:ies:normalize is enabled, and then used as a scaling
        factor on the returned luminance:


        <center><b>
                𝛳<sub>light</sub>, 𝜙 =
                    toPolarCoordinates(emissionDirectionInLightSpace)

            𝛳<sub>ies</sub> = applyAngleScale(𝛳<sub>light</sub>, angleScale)

                    iesSample = sampleIES(iesFile, 𝛳<sub>ies</sub>, 𝜙)

             iesNormalize ⟹ iesSample = iesSample ⋅ iesProfilePower(iesFile)

                    L<sub>Color</sub> = iesSample ⋅ L<sub>Color</sub>
        </b></center>

        See `inputs:shaping:ies:angleScale` for a description of
        `applyAngleScale`, and `inputs:shaping:ies:normalize` for how
        `iesProfilePower` is calculated.

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "IES Profile",
            "customData": {
                "apiName": "shaping:ies:file"
            }
        }
    )
    inputs.shaping.ies.angleScale = Attribute(float,
        doc="""Rescales the angular distribution of the IES profile.

        Applies a scaling factor to the latitudinal theta/vertical polar
        coordinate before sampling the IES profile, to shift the samples more
        toward the "top" or "bottom" of the profile. The scaling origin varies
        depending on whether `angleScale` is positive or negative. If it is
        positive, the scaling origin is theta = 0. If it is negative, the
        scaling origin is theta = pi (180 degrees).  Values where
        |angleScale| < 1 will "shrink" the angular range in which the
        iesProfile is applied, while values where |angleScale| > 1 will
        "grow" the angular range to which the iesProfile is mapped.

        If <i>𝛳<sub>light</sub></i> is the latitudinal theta polar
        coordinate of the emission direction in the light's local space, and
        <em>𝛳<sub>ies</sub></em> is the value that will be used when
        actually sampling the profile, then the exact formula is:

        * <i>if angleScale > 0:</i>
        <center><b>
                𝛳<sub>ies</sub> = 𝛳<sub>light</sub> / angleScale
        </b></center>

        * <i>if angleScale = 0:</i>
        <center><b>
                𝛳<sub>ies</sub> = 𝛳<sub>light</sub>
        </b></center>

        * <i>if angleScale < 0:</i>
        <center><b>
                𝛳<sub>ies</sub> = (𝛳<sub>light</sub> - π) / -angleScale + π
        </b></center>

        Usage guidelines for artists / lighting TDs:

        **If you have an IES profile for a spotlight aimed "down":**

        - You should use a positive angleScale (> 0).
        - Values where 0 < angleScale < 1 will narrow the spotlight beam.
        - Values where angleScale > 1 will broaden the spotlight beam.

        For example, if the original IES profile is a downward spotlight with
        a total cone angle of 60°, then angleScale = .5 will narrow it to
        have a cone angle of 30°, and an angleScale of 1.5 will broaden it
        to have a cone angle of 90°.

        **If you have an IES profile for a spotlight aimed "up":**

        - You should use a negative angleScale (< 0).
        - Values where -1 < angleScale < 0 will narrow the spotlight beam.
        - Values where angleScale < -1 will broaden the spotlight beam.

        For example, if the original IES profile is an upward spotlight with
        a total cone angle of 60°, then angleScale = -.5 will narrow it to
        have a cone angle of 30°, and an angleScale of -1.5 will broaden
        it to have a cone angle of 90°.

        **If you have an IES profile that's isn't clearly "aimed" in a single
        direction, OR it's aimed in a direction other than straight up or
        down:**

        - Applying angleScale will alter the vertical angle mapping for your
          IES light, but it may be difficult to have a clear intuitive sense
          of how varying the angleScale will affect the shape of your light

        If you violate the above rules (i.e., use a negative angleScale for a
        spotlight aimed down), then angleScale will still alter the vertical-
        angle mapping, but in more non-intuitive ways (i.e., broadening /
        narrowing may seem inverted, and the IES profile may seem to "translate"
        through the vertical angles, rather than uniformly scale).

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "Profile Scale",
            "customData": {
                "apiName": "shaping:ies:angleScale"
            }
        }
    )
    inputs.shaping.ies.normalize = Attribute(bool,
        doc="""Normalizes the IES profile so that it affects the shaping
        of the light while preserving the overall energy output.

        The sampled luminous intensity is scaled by the overall power of the
        IES profile if this is on, where the total power is calculated by
        integrating the luminous intensity over all solid angle patches
        defined in the profile.

        """,
        metadata={
            "displayGroup": "Shaping",
            "displayName": "Profile Normalization",
            "customData": {
                "apiName": "shaping:ies:normalize"
            }
        }
    )
