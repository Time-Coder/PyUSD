from ..api_schema_base import APISchemaBase
from ..dtypes import namespace
from .physics import Physics


class PhysicsCollisionAPI(APISchemaBase):
    """Applies collision attributes to a UsdGeomXformable prim. If a 
    simulation is running, this geometry will collide with other geometries that 
    have PhysicsCollisionAPI applied. If any prim in the parent hierarchy has
    the RigidBodyAPI applied, the collider is considered a part of the closest
    ancestor body. If there is no body in the parent hierarchy, this collider
    is considered to be static.
    """

    @property
    def physics(self) -> Physics: ...

