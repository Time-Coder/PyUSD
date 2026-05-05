from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import float3
from typing import List


class Radiance(Attribute):

    @property
    def sphericalHarmonicsDegree(self)->Attribute[int]:
        """The highest degree of the spherical harmonics. A degree of N
        implies a coefficient element size (per particle) of (N+1)*(N+1) values.
        The spherical harmonics degree is the same for all particles in the
        ParticleField."""

    @sphericalHarmonicsDegree.setter
    def sphericalHarmonicsDegree(self, value:int)->None: ...

    @property
    def sphericalHarmonicsCoefficients(self)->Attribute[List[float3]]:
        """Flattened array of SH coefficients.
        The SH coefficients are grouped in the array by particle, meaning each
        particle has N contiguous coefficients, Y(m,l) sorted first by order (m)
        and then within the order by index (l). A renderer can compute an
        element size per particle based on the SH degree, and use that to stripe
        the array by particle."""

    @sphericalHarmonicsCoefficients.setter
    def sphericalHarmonicsCoefficients(self, value:List[float3])->None: ...

    @property
    def sphericalHarmonicsCoefficientsh(self)->Attribute[List[half3]]:
        """Flattened array of SH coefficients.
        The SH coefficients are grouped in the array by particle, meaning each
        particle has N contiguous coefficients, Y(m,l) sorted first by order (m)
        and then within the order by index (l). A renderer can compute an
        element size per particle based on the SH degree, and use that to stripe
        the array by particle.

        If the float precision version is available it should be preferred."""

    @sphericalHarmonicsCoefficientsh.setter
    def sphericalHarmonicsCoefficientsh(self, value:List[half3])->None: ...
