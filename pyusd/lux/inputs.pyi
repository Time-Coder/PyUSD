from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import color3f
from ..dtypes import asset, token
from typing import List


class Inputs(Attribute):

    class Format(token):
        Automatic = "automatic"
        Latlong = "latlong"
        MirroredBall = "mirroredBall"
        Angular = "angular"
        CubeMapVerticalCross = "cubeMapVerticalCross"


    @property
    def intensity(self)->Attribute[float]:
        """Scales the brightness of the light linearly.

        Expresses the "base", unmultiplied luminance emitted (L) of the light,
        in nits (cd∕m²):

        <center><b>
                        L<sub>Scalar</sub> = intensity
        </b></center>

        Normatively, the lights' emission is in units of spectral radiance
        normalized such that a directly visible light with `intensity` 1 and
        `exposure` 0 normally incident upon the sensor plane will generate a
        pixel value of [1, 1, 1] in an RGB renderer, and thus have a luminance
        of 1 nit. A light with `intensity` 2 and `exposure` 0 would therefore
        have a luminance of 2 nits.
        """

    @intensity.setter
    def intensity(self, value:float)->None: ...

    @property
    def exposure(self)->Attribute[float]:
        """Scales the brightness of the light exponentially as a power
        of 2 (similar to an F-stop control over exposure).  The result
        is multiplied against the intensity:

        <center><b>
                L<sub>Scalar</sub> = L<sub>Scalar</sub> ⋅ 2<sup>exposure</sup>
        </b></center>

        Normatively, the lights' emission is in units of spectral radiance
        normalized such that a directly visible light with `intensity` 1 and
        `exposure` 0 normally incident upon the sensor plane will generate a
        pixel value of [1, 1, 1] in an RGB renderer, and thus have a luminance
        of 1 nit (cd∕m²). A light with `intensity` 1 and `exposure` 2 would
        therefore have a luminance of 4 nits.
        """

    @exposure.setter
    def exposure(self, value:float)->None: ...

    @property
    def diffuse(self)->Attribute[float]:
        """A multiplier for the effect of this light on the diffuse
        response of materials.  This is a non-physical control."""

    @diffuse.setter
    def diffuse(self, value:float)->None: ...

    @property
    def specular(self)->Attribute[float]:
        """A multiplier for the effect of this light on the specular
        response of materials.  This is a non-physical control."""

    @specular.setter
    def specular(self, value:float)->None: ...

    @property
    def normalize(self)->Attribute[bool]:
        """Normalizes the emission such that the power of the light
        remains constant while altering the size of the light, by dividing the
        luminance by the world-space surface area of the light.

        This makes it easier to independently adjust the brightness and size
        of the light, by causing the total illumination provided by a light to
        not vary with the area or angular size of the light.

        Mathematically, this means that the luminance of the light will be
        divided by a factor representing the "size" of the light:

        <center><b>
                        L<sub>Scalar</sub> = L<sub>Scalar</sub> / sizeFactor
        </b></center>

        ...where `sizeFactor` = 1 if `normalize` is off, and is calculated
        depending on the family of the light as described below if `normalize`
        is on.

        ### DomeLight / PortalLight:

        For a dome light (and its associated PortalLight), this attribute is
        ignored:

        <center><b>
                        sizeFactor<sub>dome</sub> = 1
        </b></center>

        ### Area Lights:

        For an area light, the `sizeFactor` is the surface area (in world
        space) of the shape of the light, including any scaling applied to the
        light by its transform stack. This includes the boundable light types
        which have a calculable surface area:

        - MeshLightAPI
        - DiskLight
        - RectLight
        - SphereLight
        - CylinderLight

        <center><b>
                        sizeFactor<sub>area</sub> = worldSpaceSurfaceArea(light)
        </b></center>

        ### DistantLight:

        For distant lights, we first define 𝛳<sub>max</sub> as:

        <center><b>
                𝛳<sub>max</sub> = clamp(toRadians(distantLightAngle) / 2, 0, 𝜋)
        </b></center>

        Then we use the following formula:

        * <i>if 𝛳<sub>max</sub> = 0:</i>
        <center><b>
                sizeFactor<sub>distant</sub> = 1
        </b></center>

        * <i>if 0 < 𝛳<sub>max</sub> ≤ 𝜋 / 2:</i>
        <center><b>
            sizeFactor<sub>distant</sub> = sin²𝛳<sub>max</sub> ⋅ 𝜋
        </b></center>

        * <i>if 𝜋 / 2 < 𝛳<sub>max</sub> ≤ 𝜋:</i>
        <center><b>
                    sizeFactor<sub>distant</sub> =
                        (2 - sin²𝛳<sub>max</sub>) ⋅ 𝜋
        </b></center>

        This formula is used because it satisfies the following two properties:

        1. When normalize is enabled, the received illuminance from this light
           on a surface normal to the light's primary direction is held constant
           when angle changes, and the "intensity" property becomes a measure of
           the illuminance, expressed in lux, for a light with 0 exposure.

        2. If we assume that our distant light is an approximation for a "very
           far" sphere light (like the sun), then (for
           *0 < 𝛳<sub>max</sub> ≤ 𝜋/2*) this definition agrees with the
           definition used for area lights - i.e., the total power of this distant
           sphere light is constant when the "size" (i.e., angle) changes, and our
           sizeFactor is proportional to the total surface area of this sphere.

        ### Other Lights

        The above taxonomy describes behavior for all built-in light types.
        (Note that the above is based on schema *family* - i.e., `DomeLight_1`
        follows the rules for a `DomeLight`, and ignores `normalize`).

        Lights from other third-party plugins / schemas must document their
        expected behavior with regards to normalize.  However, some general
        guidelines are:

        - Lights that either inherit from or are strongly associated with one of
          the built-in types should follow the behavior of the built-in type
          they inherit/resemble; i.e., a renderer-specific "MyRendererRectLight"
          should have its size factor be its world-space surface area.
        - Lights that are boundable and have a calculable surface area should
          follow the rules for an Area Light, and have their sizeFactor be their
          world-space surface area.
        - Lights that are non-boundable and/or have no way to concretely or even
          "intuitively" associate them with a "size" will ignore this attribute
          (and always set sizeFactor = 1).

        Lights that don't clearly meet any of the above criteria may either
        ignore the normalize attribute or try to implement support using
        whatever heuristic seems to make sense. For instance,
        MyMandelbulbLight might use a sizeFactor equal to the world-space
        surface area of a sphere which "roughly" bounds it.
        """

    @normalize.setter
    def normalize(self, value:bool)->None: ...

    @property
    def color(self)->Attribute[color3f]:
        """The color of emitted light, in the rendering color space.

        This color is just multiplied with the emission:

        <center><b>
                        L<sub>Color</sub> = L<sub>Scalar</sub> ⋅ color
        </b></center>

        In the case of a spectral renderer, this color should be uplifted such
        that it round-trips to within the limit of numerical accuracy under the
        rendering illuminant. We recommend the use of a rendering color space
        well defined in terms of a Illuminant D illuminant (ideally a D
        illuminant whose white point has a well-defined spectral representation,
        such as D65), to avoid unspecified uplift. See: \\ref usdLux_quantities
        """

    @color.setter
    def color(self, value:color3f)->None: ...

    @property
    def enableColorTemperature(self)->Attribute[bool]:
        """Enables using colorTemperature."""

    @enableColorTemperature.setter
    def enableColorTemperature(self, value:bool)->None: ...

    @property
    def colorTemperature(self)->Attribute[float]:
        """Color temperature, in degrees Kelvin, representing the
        white point.  The default is a common white point, D65.  Lower
        values are warmer and higher values are cooler.  The valid range
        is from 1000 to 10000. Only takes effect when
        enableColorTemperature is set to true.  When active, the
        computed result multiplies against the color attribute.
        See UsdLuxBlackbodyTemperatureAsRgb().

        This is always calculated as an RGB color using a D65 white point,
        regardless of the rendering color space, normalized such that the
        default value of 6500 will always result in white, and then should be
        transformed to the rendering color space.

        Spectral renderers should do the same and then uplift the resulting
        color after multiplying with the `color` attribute.  We recommend the
        use of a rendering color space well defined in terms of a Illuminant D
        illuminant, to avoid unspecified uplift.  See: \\ref usdLux_quantities
        """

    @colorTemperature.setter
    def colorTemperature(self, value:float)->None: ...

    @property
    def focus(self)->Attribute[float]:
        """A control to shape the spread of light.  Higher focus
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
        """

    @focus.setter
    def focus(self, value:float)->None: ...

    @property
    def focusTint(self)->Attribute[color3f]:
        """Off-axis color tint.  This tints the emission in the
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
        """

    @focusTint.setter
    def focusTint(self, value:color3f)->None: ...

    @property
    def angle(self)->Attribute[float]:
        """Angular limit off the primary axis to restrict the light
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
        """

    @angle.setter
    def angle(self, value:float)->None: ...

    @property
    def softness(self)->Attribute[float]:
        """Controls the cutoff softness for cone angle.

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
        """

    @softness.setter
    def softness(self, value:float)->None: ...

    @property
    def file(self)->Attribute[asset]:
        """An IES (Illumination Engineering Society) light
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
        """

    @file.setter
    def file(self, value:asset)->None: ...

    @property
    def angleScale(self)->Attribute[float]:
        """Rescales the angular distribution of the IES profile.

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
        """

    @angleScale.setter
    def angleScale(self, value:float)->None: ...

    @property
    def normalize(self)->Attribute[bool]:
        """Normalizes the IES profile so that it affects the shaping
        of the light while preserving the overall energy output.

        The sampled luminous intensity is scaled by the overall power of the
        IES profile if this is on, where the total power is calculated by
        integrating the luminous intensity over all solid angle patches
        defined in the profile.
        """

    @normalize.setter
    def normalize(self, value:bool)->None: ...

    @property
    def enable(self)->Attribute[bool]:
        """Enables shadows to be cast by this light."""

    @enable.setter
    def enable(self, value:bool)->None: ...

    @property
    def color(self)->Attribute[color3f]:
        """The color of shadows cast by the light.  This is a
        non-physical control.  The default is to cast black shadows."""

    @color.setter
    def color(self, value:color3f)->None: ...

    @property
    def distance(self)->Attribute[float]:
        """The maximum distance shadows are cast. The distance is
        measured as the distance between the point on the surface and the 
        occluder.
        The default value (-1) indicates no limit.
        """

    @distance.setter
    def distance(self, value:float)->None: ...

    @property
    def falloff(self)->Attribute[float]:
        """The size of the shadow falloff zone within the shadow max 
        distance, which can be used to hide the hard cut-off for shadows seen 
        stretching past the max distance. The falloff zone is the area that 
        fades from full shadowing at the beginning of the falloff zone to no 
        shadowing at the max distance from the occluder. The falloff zone 
        distance cannot exceed the shadow max distance. A falloff value equal 
        to or less than zero (with -1 as the default) indicates no falloff. 
        """

    @falloff.setter
    def falloff(self, value:float)->None: ...

    @property
    def falloffGamma(self)->Attribute[float]:
        """A gamma (i.e., exponential) control over shadow strength
        with linear distance within the falloff zone. This controls the rate
        of the falloff.
        This requires the use of shadowDistance and shadowFalloff."""

    @falloffGamma.setter
    def falloffGamma(self, value:float)->None: ...

    @property
    def angle(self)->Attribute[float]:
        """Angular diameter of the light in degrees.
        As an example, the Sun is approximately 0.53 degrees as seen from Earth.
        Higher values broaden the light and therefore soften shadow edges.

        This value is assumed to be in the range `0 <= angle < 360`, and will
        be clipped to this range. Note that this implies that we can have a
        distant light emitting from more than a hemispherical area of light
        if angle > 180. While this is valid, it is possible that for large
        angles a DomeLight may provide better performance. If angle is 0, the
        DistantLight represents a perfectly parallel light source.
        """

    @angle.setter
    def angle(self, value:float)->None: ...

    @property
    def radius(self)->Attribute[float]:
        """Radius of the disk."""

    @radius.setter
    def radius(self, value:float)->None: ...

    @property
    def width(self)->Attribute[float]:
        """Width of the rectangle, in the local X axis."""

    @width.setter
    def width(self, value:float)->None: ...

    @property
    def height(self)->Attribute[float]:
        """Height of the rectangle, in the local Y axis."""

    @height.setter
    def height(self, value:float)->None: ...

    @property
    def file(self)->Attribute[asset]:
        """A color texture to use on the rectangle."""

    @file.setter
    def file(self, value:asset)->None: ...

    @property
    def length(self)->Attribute[float]:
        """Length of the cylinder, in the local X axis."""

    @length.setter
    def length(self, value:float)->None: ...

    @property
    def format(self)->Attribute[Format]:
        """
        Specifies the parameterization of the color map file.
        Valid values are:
        - automatic: Tries to determine the layout from the file itself.
          For example, Renderman texture files embed an explicit
          parameterization.
        - latlong: Latitude as X, longitude as Y.
        - mirroredBall: An image of the environment reflected in a
          sphere, using an implicitly orthogonal projection.
        - angular: Similar to mirroredBall but the radial dimension
          is mapped linearly to the angle, providing better sampling
          at the edges.
        - cubeMapVerticalCross: A cube map with faces laid out as a
          vertical cross.
        """

    @format.setter
    def format(self, value:Format)->None: ...
