from enum import ReprEnum

from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token


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

    class Approximation(token, ReprEnum):
        None_ = "none"
        ConvexDecomposition = "convexDecomposition"
        ConvexHull = "convexHull"
        BoundingSphere = "boundingSphere"
        BoundingCube = "boundingCube"
        MeshSimplification = "meshSimplification"


    physics: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    physics.approximation = AttributeSpec(Approximation,
        uniform=True,
        value="none",
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
