from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


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


    class MaterialSyncMode(token):
        MaterialGlowTintsLight = "materialGlowTintsLight"
        Independent = "independent"
        NoMaterialResponse = "noMaterialResponse"

    @property
    def inputs(self) -> Inputs: ...

    @property
    def collection(self) -> Collection: ...

    @property
    def light(self) -> Light: ...

