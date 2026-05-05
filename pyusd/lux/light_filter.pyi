from ..geom.xformable import Xformable
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


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
    def lightFilter(self) -> LightFilter: ...

