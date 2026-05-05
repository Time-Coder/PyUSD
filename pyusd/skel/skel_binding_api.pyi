from ..api_schema_base import APISchemaBase
from ..gf import matrix4d
from ..dtypes import namespace, token
from .primvars import Primvars
from .skel import Skel


class SkelBindingAPI(APISchemaBase):
    """Provides API for authoring and extracting all the skinning-related
    data that lives in the "geometry hierarchy" of prims and models that want
    to be skeletally deformed.
    
    See the extended \\ref UsdSkel_BindingAPI "UsdSkelBindingAPI schema"
    documentation for more about bindings and how they apply in a scene graph.
    
    """


    class SkinningMethod(token):
        ClassicLinear = "classicLinear"
        DualQuaternion = "dualQuaternion"

    @property
    def primvars(self) -> Primvars: ...

    @property
    def skel(self) -> Skel: ...

