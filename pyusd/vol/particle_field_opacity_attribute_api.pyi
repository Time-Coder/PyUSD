from ..api_schema_base import APISchemaBase
from ..gf import half
from .radiance import Radiance


class ParticleFieldOpacityAttributeAPI(APISchemaBase):
    """A ParticleField related applied schema that provides an
    opacities attribute to define the opacity of the particles.
    
    The opacity here should be in the range [0, 1], and inline with the
    traditional (linear) sense of computer graphics opacity, not the
    transformed data sometimes seen in PLY files associated with
    gaussian splats, where the values need to be processed with a
    sigmoid activation function.
    
    Attributes are provided in both `float` and `half` types for some
    easy data footprint affordance, data consumers should prefer
    `float` version if available.
    
    The length of this attribute is expected to match the length of
    the provided position data. If it is too long it will be truncated
    to the number of particles define by the position data. If it is
    too short it will be ignored.
    
    If it is ignored or not populated, then the default value of fully
    opaque (1.0) should be used.
    
    """

    @property
    def opacities(self)->Attribute[List[float]]:
        """Opacity for each particle."""

    @opacities.setter
    def opacities(self, value:List[float])->None: ...

    @property
    def opacitiesh(self)->Attribute[List[half]]:
        """Opacity for each particle. If the float precision version is
                available it should be preferred."""

    @opacitiesh.setter
    def opacitiesh(self, value:List[half])->None: ...

