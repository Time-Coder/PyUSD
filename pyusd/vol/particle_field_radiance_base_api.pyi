from ..api_schema_base import APISchemaBase
from .radiance import Radiance


class ParticleFieldRadianceBaseAPI(APISchemaBase):
    """Defines a base-class type applied schema that all applied schema
    that provides a ParticleField radiance definition will automatically
    apply.
    The purpose of this base class is to allow validation to enforce
    that a radiance definition is present for a ParticleField
    """

