from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace
from ..gf import color3f
from ..dtypes import token
from ..common import SchemaKind


class LightAPI(APISchemaBase):
    """API schema that imparts the quality of being a light onto a prim. 
    
    A light is any prim that has this schema applied to it.  This is true 
    regardless of whether LightAPI is included as a built-in API of the prim 
    type (e.g. RectLight or DistantLight) or is applied directly to a Gprim 
    that should be treated as a light.
    
    <b>Quantities and Units</b>
    
    Most renderers consuming OpenUSD today are RGB renderers, rather than
    spectral. Units in RGB renderers are tricky to define as each of the red,
    green and blue channels transported by the renderer represents the
    convolution of a spectral exposure distribution, e.g. CIE Illuminant D65,
    with a sensor response function, e.g. CIE 1931 𝓍̅. Thus the main quantity
    in an RGB renderer is neither radiance nor luminance, but "integrated
    radiance" or "tristimulus weight".
    
    The emission of a default light with `intensity` 1 and `color` [1, 1, 1] is
    an Illuminant D spectral distribution with chromaticity matching the
    rendering color space white point, normalized such that a ray normally
    incident upon the sensor with EV0 exposure settings will generate a pixel
    value of [1, 1, 1] in the rendering color space.
    
    Given the above definition, that means that the luminance of said default
    light will be 1 *nit (cd∕m²)* and its emission spectral radiance
    distribution is easily computed by appropriate normalization.
    
    For brevity, the term *emission* will be used in the documentation to mean
    "emitted spectral radiance" or "emitted integrated radiance/tristimulus
    weight", as appropriate.
    
    The method of "uplifting" an RGB color to a spectral distribution is
    unspecified other than that it should round-trip under the rendering
    illuminant to the limits of numerical accuracy.
    
    Note that some color spaces, most notably ACES, define their white points
    by chromaticity coordinates that do not exactly line up to any value of a
    standard illuminant. Because we do not define the method of uplift beyond
    the round-tripping requirement, we discourage the use of such color spaces
    as the rendering color space, and instead encourage the use of color spaces
    whose white point has a well-defined spectral representation, such as D65.
    
    <b>Linking</b>
    
    Lights can be linked to geometry.  Linking controls which geometry
    a light illuminates, and which geometry casts shadows from the light.
    
    Linking is specified as collections (UsdCollectionAPI) which can
    be accessed via GetLightLinkCollection() and GetShadowLinkCollection().
    Note that these collections have their includeRoot set to true,
    so that lights will illuminate and cast shadows from all objects
    by default.  To illuminate only a specific set of objects, there
    are two options.  One option is to modify the collection paths
    to explicitly exclude everything else, assuming it is known;
    the other option is to set includeRoot to false and explicitly
    include the desired objects.  These are complementary approaches
    that may each be preferable depending on the scenario and how
    to best express the intent of the light setup.
    
    <b>Encapsulation</b>
    A prim with LightAPI applied must not be parented under a
    UsdShadeConnectable prim, with the exception of prims which themselves have
    UsdLuxLightAPI applied. Some lighting scenarios require light prims to be 
    parented under other light prims. For example, a DomeLight might contain
    PortalLight children to refine the lighting for a particular scene.
    
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "extraPlugInfo": {
                "providesUsdShadeConnectableAPIBehavior": None
            },
            "extraIncludes": """
    #include "pxr/usd/usd/collectionAPI.h"
    #include "pxr/usd/usdShade/input.h"
    #include "pxr/usd/usdShade/output.h" """
        }
    }

    class MaterialSyncMode(token):
        MaterialGlowTintsLight = "materialGlowTintsLight"
        Independent = "independent"
        NoMaterialResponse = "noMaterialResponse"


    collection: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    collection.lightLink.includeRoot = Attribute(bool,
        uniform=True,
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )
    collection.shadowLink.includeRoot = Attribute(bool,
        uniform=True,
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        doc="""Default ID for the light's shader. 
        This defines the shader ID for this light when a render context specific
        shader ID is not available. 

        The default shaderId for the intrinsic UsdLux lights (RectLight, 
        DistantLight, etc.) are set to default to the light's type name. For 
        each intrinsic UsdLux light, we will always register an SdrShaderNode in
        the SdrRegistry, with the identifier matching the type name and the 
        source type "USD", that corresponds to the light's inputs.
        \\see GetShaderId
        \\see GetShaderIdAttrForRenderContext
        \\see SdrRegistry::GetShaderNodeByIdentifier
        \\see SdrRegistry::GetShaderNodeByIdentifierAndType

        """,
        metadata={
            "displayGroup": "Internal",
            "customData": {
                "apiName": "shaderId"
            }
        }
    )
    light.materialSyncMode = Attribute(MaterialSyncMode,
        uniform=True,
        doc="""
        For a LightAPI applied to geometry that has a bound Material, 
        which is entirely or partly emissive, this specifies the relationship 
        of the Material response to the lighting response.
        Valid values are:
        - materialGlowTintsLight: All primary and secondary rays see the 
          emissive/glow response as dictated by the bound Material while the 
          base color seen by light rays (which is then modulated by all of the 
          other LightAPI controls) is the multiplication of the color feeding 
          the emission/glow input of the Material (i.e. its surface or volume 
          shader) with the scalar or pattern input to *inputs:color*.
          This allows the light's color to tint the geometry's glow color while 
          preserving access to intensity and other light controls as ways to 
          further modulate the illumination.
        - independent: All primary and secondary rays see the emissive/glow 
          response as dictated by the bound Material, while the base color seen 
          by light rays is determined solely by *inputs:color*. Note that for 
          partially emissive geometry (in which some parts are reflective 
          rather than emissive), a suitable pattern must be connected to the 
          light's color input, or else the light will radiate uniformly from 
          the geometry.
        - noMaterialResponse: The geometry behaves as if there is no Material
          bound at all, i.e. there is no diffuse, specular, or transmissive 
          response. The base color of light rays is entirely controlled by the
          *inputs:color*. This is the standard mode for "canonical" lights in 
          UsdLux and indicates to renderers that a Material will either never 
          be bound or can always be ignored.

        """,
        metadata={
            "displayGroup": "Geometry",
            "displayName": "Material Sync Mode",
            "customData": {
                "apiName": "materialSyncMode"
            }
        }
    )

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.intensity = Attribute(float,
        doc="""Scales the brightness of the light linearly.

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

        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Intensity",
            "customData": {
                "apiName": "intensity"
            }
        }
    )
    inputs.exposure = Attribute(float,
        doc="""Scales the brightness of the light exponentially as a power
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

        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Exposure",
            "customData": {
                "apiName": "exposure"
            }
        }
    )
    inputs.diffuse = Attribute(float,
        doc="""A multiplier for the effect of this light on the diffuse
        response of materials.  This is a non-physical control.
        """,
        metadata={
            "displayGroup": "Refine",
            "displayName": "Diffuse Multiplier",
            "customData": {
                "apiName": "diffuse"
            }
        }
    )
    inputs.specular = Attribute(float,
        doc="""A multiplier for the effect of this light on the specular
        response of materials.  This is a non-physical control.
        """,
        metadata={
            "displayGroup": "Refine",
            "displayName": "Specular Multiplier",
            "customData": {
                "apiName": "specular"
            }
        }
    )
    inputs.normalize = Attribute(bool,
        doc="""Normalizes the emission such that the power of the light
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

        """,
        metadata={
            "displayGroup": "Advanced",
            "displayName": "Normalize Power",
            "customData": {
                "apiName": "normalize"
            }
        }
    )
    inputs.color = Attribute(color3f,
        doc="""The color of emitted light, in the rendering color space.

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

        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Color",
            "customData": {
                "apiName": "color"
            }
        }
    )
    inputs.enableColorTemperature = Attribute(bool,
        doc="Enables using colorTemperature.",
        metadata={
            "displayGroup": "Basic",
            "displayName": "Enable Color Temperature",
            "customData": {
                "apiName": "enableColorTemperature"
            }
        }
    )
    inputs.colorTemperature = Attribute(float,
        doc="""Color temperature, in degrees Kelvin, representing the
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

        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Color Temperature",
            "customData": {
                "apiName": "colorTemperature"
            }
        }
    )
    light.filters = Relationship(
        doc="Relationship to the light filters that apply to this light.",
        metadata={
            "customData": {
                "apiName": "filters"
            }
        }
    )
