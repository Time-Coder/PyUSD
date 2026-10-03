from .api_schema_base import APISchemaBase
from .attribute_spec import AttributeSpec
from .gf import float2

class ColorSpaceDefinitionAPI(APISchemaBase):
    """UsdColorSpaceDefinitionAPI is an API schema for defining a custom
    color space. Custom color spaces become available for use on prims or for
    assignment to attributes via the colorSpace:name property on prims that have
    applied `UsdColorSpaceAPI`. Since color spaces inherit hierarchically, a
    custom color space defined on a prim will be available to all descendants of
    that prim, unless overridden by a more local color space definition bearing
    the same name. Locally redefining color spaces within the same layer could
    be confusing, so that practice is discouraged.

    The default color space values are equivalent to an identity transform, so
    applying this schema and invoking `UsdColorSpaceAPI::ComputeColorSpace()`
    on a prim resolving to a defaulted color definition will return a color
    space equivalent to the identity transform.

    """

    @property
    def redChroma(self)->AttributeSpec[float2]:
        """Red chromaticity coordinates"""

    @redChroma.setter
    def redChroma(self, value:float2)->None: ...

    @property
    def greenChroma(self)->AttributeSpec[float2]:
        """Green chromaticity coordinates"""

    @greenChroma.setter
    def greenChroma(self, value:float2)->None: ...

    @property
    def blueChroma(self)->AttributeSpec[float2]:
        """Blue chromaticity coordinates"""

    @blueChroma.setter
    def blueChroma(self, value:float2)->None: ...

    @property
    def whitePoint(self)->AttributeSpec[float2]:
        """Whitepoint chromaticity coordinates"""

    @whitePoint.setter
    def whitePoint(self, value:float2)->None: ...

    @property
    def gamma(self)->AttributeSpec[float]:
        """Gamma value of the log section"""

    @gamma.setter
    def gamma(self, value:float)->None: ...

    @property
    def linearBias(self)->AttributeSpec[float]:
        """Linear bias of the log section"""

    @linearBias.setter
    def linearBias(self, value:float)->None: ...
