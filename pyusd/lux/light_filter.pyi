from ..attribute_spec import AttributeSpec
from ..dtypes import token
from ..geom.xformable import Xformable
from .collection import Collection

class LightFilter(Xformable):
    """A light filter modifies the effect of a light.
    Lights refer to filters via relationships so that filters may be
    shared.

    <b>Linking</b>

    Filters can be linked to geometry.  Linking controls which geometry
    a light-filter affects, when considering the light filters attached
    to a light illuminating the geometry.

    Linking is specified as a collection (UsdCollectionAPI) which can
    be accessed via GetFilterLinkCollection().

    <b>Encapsulation</b>

    UsdLuxLightFilter must not be parented under a UsdShadeMaterial.
    See \\ref usdLux_Encapsulation for more details.

    """

    @property
    def collection(self) -> Collection: ...

    @property
    def shaderId(self)->AttributeSpec[token]:
        """Default ID for the light filter's shader.
        This defines the shader ID for this light filter when a render context
        specific shader ID is not available.

        \\see GetShaderId
        \\see GetShaderIdAttrForRenderContext
        \\see SdrRegistry::GetShaderNodeByIdentifier
        \\see SdrRegistry::GetShaderNodeByIdentifierAndType
        """

    @shaderId.setter
    def shaderId(self, value:token)->None: ...
