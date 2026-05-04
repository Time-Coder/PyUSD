from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace, token
from .physics import Physics

class PhysicsMeshCollisionAPI(APISchemaBase):

    class Approximation(token):
        None_ = "none"
        ConvexDecomposition = "convexDecomposition"
        ConvexHull = "convexHull"
        BoundingSphere = "boundingSphere"
        BoundingCube = "boundingCube"
        MeshSimplification = "meshSimplification"

    @property
    def physics(self) -> Physics: ...

