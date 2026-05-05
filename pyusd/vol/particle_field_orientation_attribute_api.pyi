from ..api_schema_base import APISchemaBase
from ..gf import quatf, quath
from .radiance import Radiance


class ParticleFieldOrientationAttributeAPI(APISchemaBase):
    """A ParticleField related applied schema that provides an
    orientations attribute to define the orientation of the particles.
    
    Attributes are provided in both `float` and `half` types for some
    easy data footprint affordance, data consumers should prefer
    `float` version if available.
    
    The length of this attribute is expected to match the length of
    the provided position data. If it is too long it will be truncated
    to the number of particles define by the position data. If it is
    too short it will be ignored.
    
    If the attribute is ignored or not populated, then a default value
    of no rotation should be applied to the kernel instantiated at each
    particle.
    """

    @property
    def orientations(self)->Attribute[List[quatf]]:
        """Quaternion orientation for each particle."""

    @orientations.setter
    def orientations(self, value:List[quatf])->None: ...

    @property
    def orientationsh(self)->Attribute[List[quath]]:
        """Quaternion orientation for each particle. If the float
                precision version is defined it should be preferred."""

    @orientationsh.setter
    def orientationsh(self, value:List[quath])->None: ...

