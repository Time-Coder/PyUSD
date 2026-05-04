from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class PhysicsMeshCollisionAPI(APISchemaBase):
    """Attributes to control how a Mesh is made into a collider.
    Can be applied to only a USDGeomMesh in addition to its
    PhysicsCollisionAPI.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "MeshCollisionAPI"
        }
    }

    class Approximation(token):
        None_ = "none"
        ConvexDecomposition = "convexDecomposition"
        ConvexHull = "convexHull"
        BoundingSphere = "boundingSphere"
        BoundingCube = "boundingCube"
        MeshSimplification = "meshSimplification"


    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.approximation = Attribute(Approximation,
        uniform=True,
        doc="""Determines the mesh's collision approximation:
        "none" - The mesh geometry is used directly as a collider without any 
           approximation.
        "convexDecomposition" - A convex mesh decomposition is performed. This 
           results in a set of convex mesh colliders.
        "convexHull" - A convex hull of the mesh is generated and used as the 
           collider.
        "boundingSphere" - A bounding sphere is computed around the mesh and used 
           as a collider.
        "boundingCube" - An optimally fitting box collider is computed around the 
           mesh.
        "meshSimplification" - A mesh simplification step is performed, resulting 
           in a simplified triangle mesh collider.
        """,
        metadata={
            "customData": {
                "apiName": "approximation"
            },
            "displayName": "Approximation"
        }
    )
