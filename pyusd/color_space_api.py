from .prim import Prim
from .attribute import Attribute
from .dtypes import token, namespace
from .api_schema_base import APISchemaBase
from .common import SchemaKind


class ColorSpaceAPI(APISchemaBase):
    """UsdColorSpaceAPI is an API schema that introduces a `colorSpace`
    property for authoring scene referred color space opinions. It also provides
    a mechanism to determine the applicable color space within a scope through
    inheritance. Accordingly, this schema may be applied to any prim to 
    introduce a color space at any point in a compositional hierarchy.

    Color space resolution involves determining the color space authored on an
    attribute by first examining the attribute itself for a color space which
    may have been authored via `UsdAttribute::SetColorSpace()`. If none is found,
    the attribute's prim is checked for the existence of the `UsdColorSpaceAPI`,
    and any color space authored there. If none is found on the attribute's
    prim, the prim's ancestors are examined up the hierarchy until an authored
    color space is found. If no color space is found, an empty `TfToken` is
    returned. When no color space is found, the default color space is linear, 
    with Rec709 primaries and D65 white point, corresponding to the GfColorSpace
    token `LinearRec709`.

    For a list of built in color space token values, see `GfColorSpaceNames`.

    Use a pattern like this when determining an attribute's resolved color space:
    
    ```
    TfToken attrCs = attr.GetColorSpace();
    if (!attrCs.IsEmpty()) { 
        return attrCs; 
    }
    auto csAPI = UsdColorSpaceAPI(attr.GetPrim());
    return UsdColorSpaceAPI::ComputeColorSpaceName(attr);
    ```

    `GfColorSpace` and its associated utilities can be used to perform color 
    transformations; some examples:

    ```
    srcSpace = GfColorSpace(ComputeColorSpaceName(attr))
    targetSpace = GfColorSpace(targetSpaceName)
    targetColor = srcSpace.Convert(targetSpace, srcColor)
    srcSpace.ConvertRGBSpan(targetSpace, colorSpan)
    ```

    It is recommended that in situations where performance is a concern, an 
    application should perform conversions infrequently and cache results
    wherever possible.
    
    """

    schema_kind = SchemaKind.SingleApplyAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "extraIncludes": """
#include "pxr/base/gf/colorSpace.h"
#include "pxr/base/tf/bigRWMutex.h"
"""
        }
    }

    colorSpace: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    colorSpace.create_prop(Attribute(token, "name", uniform=True, doc=
        """The color space that applies to attributes with
        unauthored color spaces on this prim and its descendents.
        """
    ))
    