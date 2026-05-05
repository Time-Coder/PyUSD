from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, token
from .outputs import Outputs


class RiMaterialAPI(APISchemaBase):
    """
    \\deprecated Materials should use UsdShadeMaterial instead.
    This schema will be removed in a future release.
    
    This API provides outputs that connect a material prim to prman 
    shaders and RIS objects.
    """

    @property
    def outputs(self) -> Outputs: ...

