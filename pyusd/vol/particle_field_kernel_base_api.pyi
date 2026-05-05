from ..api_schema_base import APISchemaBase
from .radiance import Radiance


class ParticleFieldKernelBaseAPI(APISchemaBase):
    """Defines a base-class type applied schema that all applied schema
    that provide a ParticleField kernel will automatically apply.
    The ParticleField kernel defines the spatial basis function for each
    particle.
    The purpose of this base class is to allow validation to enforce
    that a kernel definition is present for a ParticleField
    """

