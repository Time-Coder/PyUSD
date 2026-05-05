from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..gf import float3
from ..common import SchemaKind


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

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": """'''
    #include "pxr/usd/usdVol/particleFieldRadianceBaseAPI.h"
            '''""",
            "extraIncludes": """'''
    #include "pxr/usd/usdVol/particleFieldRadianceBaseAPI.h"
            '''""",
            "reflectedAPISchemas": None
        }
    }

    radiance: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    radiance.sphericalHarmonicsDegree = Attribute(int,
        uniform=True,
        doc="""The highest degree of the spherical harmonics. A degree of N
        implies a coefficient element size (per particle) of (N+1)*(N+1) values.
        The spherical harmonics degree is the same for all particles in the
        ParticleField.
        """
    )
    radiance.sphericalHarmonicsCoefficients = Attribute(List[float3],
        doc="""Flattened array of SH coefficients.
        The SH coefficients are grouped in the array by particle, meaning each
        particle has N contiguous coefficients, Y(m,l) sorted first by order (m)
        and then within the order by index (l). A renderer can compute an
        element size per particle based on the SH degree, and use that to stripe
        the array by particle.
        """
    )
    radiance.sphericalHarmonicsCoefficientsh = Attribute(List[half3],
        doc="""Flattened array of SH coefficients.
        The SH coefficients are grouped in the array by particle, meaning each
        particle has N contiguous coefficients, Y(m,l) sorted first by order (m)
        and then within the order by index (l). A renderer can compute an
        element size per particle based on the SH degree, and use that to stripe
        the array by particle.

        If the float precision version is available it should be preferred.
        """
    )
