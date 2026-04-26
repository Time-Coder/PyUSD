from .prim import Prim
from .api_schema_base import APISchemaBase


class ColorSpaceDefinitionAPI(APISchemaBase):
    'UsdColorSpaceDefinitionAPI is an API schema for defining a custom\n    color space. Custom color spaces become available for use on prims or for\n    assignment to attributes via the colorSpace:name property on prims that have\n    applied `UsdColorSpaceAPI`. Since color spaces inherit hierarchically, a\n    custom color space defined on a prim will be available to all descendants of\n    that prim, unless overridden by a more local color space definition bearing\n    the same name. Locally redefining color spaces within the same layer could\n    be confusing, so that practice is discouraged.\n\n    The default color space values are equivalent to an identity transform, so\n    applying this schema and invoking `UsdColorSpaceAPI::ComputeColorSpace()`\n    on a prim resolving to a defaulted color definition will return a color\n    space equivalent to the identity transform.\n    '
    @classmethod
    def apply(cls, prim:Prim)->Prim: ...
