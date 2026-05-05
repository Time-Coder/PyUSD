from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, string
from .config import Config


class MaterialXConfigAPI(APISchemaBase):
    """MaterialXConfigAPI is an API schema that provides an interface for
    storing information about the MaterialX environment.
    
    Initially, it only exposes an interface to record the MaterialX library
    version that data was authored against. The intention is to use this
    information to allow the MaterialX library to perform upgrades on data
    from prior MaterialX versions.
    
    """

    @property
    def config(self) -> Config: ...

