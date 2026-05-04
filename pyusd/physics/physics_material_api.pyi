from ..api_schema_base import APISchemaBase
from ..dtypes import namespace
from .physics import Physics


class PhysicsMaterialAPI(APISchemaBase):
    """ Adds simulation material properties to a Material. All collisions 
    that have a relationship to this material will have their collision response 
    defined through this material.
    """

    @property
    def physics(self) -> Physics: ...

