from pyusd.geom.xformable import Xformable
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


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
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "providesUsdShadeConnectableAPIBehavior": "None"
            },
            "extraIncludes": """
                #include "pxr/usd/usd/collectionAPI.h"
                #include "pxr/usd/usdShade/input.h"
                #include "pxr/usd/usdShade/output.h" """
        }
    }

    collection: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    collection.filterLink.includeRoot = Attribute(bool,
        uniform=True,
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    lightFilter: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    lightFilter.shaderId = Attribute(token,
        uniform=True,
        value="",
        doc=
        """Default ID for the light filter's shader. 
        This defines the shader ID for this light filter when a render context 
        specific shader ID is not available. 

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
