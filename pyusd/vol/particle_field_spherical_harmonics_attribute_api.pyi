from ..api_schema_base import APISchemaBase
from ..gf import float3
from ..dtypes import namespace
from .radiance import Radiance


class ParticleFieldSphericalHarmonicsAttributeAPI(APISchemaBase):
    """A ParticleField related applied schema that provides spherical
    harmonics attributes to define the radiance of the particles.
    
    The spherical harmonics degree is constant across all the particles
    in the ParticleField.
    
    Attributes are provided in both `float` and `half` types for some
    easy data footprint affordance, data consumers should prefer
    `float` version if available.
    
    The length of this attribute is expected to match the length of
    the provided position data times the per-particle element size
    derived from the SH degree (specifically element size =
    (degree+1)*(degree+1)). If it is too long it will be truncated
    to the number of particles define by the position data. If it is
    too short it will be ignored.
    
    If it is ignored or not populated, the particle should use a SH
    coefficient corresponding to a DC signal of (0.5, 0.5, 0.5),
    with degree 0.
    
    """

    @property
    def radiance(self) -> Radiance: ...

