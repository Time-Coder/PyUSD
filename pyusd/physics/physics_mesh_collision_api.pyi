from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, token
from .physics import Physics


class PhysicsMeshCollisionAPI(APISchemaBase):
    """Attributes to control how a Mesh is made into a collider.
    Can be applied to only a USDGeomMesh in addition to its
    PhysicsCollisionAPI.
    """


    class Approximation(token):
        None_ = "none"
        ConvexDecomposition = "convexDecomposition"
        ConvexHull = "convexHull"
        BoundingSphere = "boundingSphere"
        BoundingCube = "boundingCube"
        MeshSimplification = "meshSimplification"

    @property
    def physics(self) -> Physics: ...

