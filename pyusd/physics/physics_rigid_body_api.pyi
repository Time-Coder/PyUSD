from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import vector3f
from ..dtypes import namespace
from .physics import Physics

class PhysicsRigidBodyAPI(APISchemaBase):
    """Applies physics body attributes to any UsdGeomXformable prim and
    marks that prim to be driven by a simulation. If a simulation is running
    it will update this prim's pose. All prims in the hierarchy below this 
    prim should move rigidly along with the body, except when the descendant
    prim has its own UsdPhysicsRigidBodyAPI (marking a separate rigid body
    subtree which moves independently of the parent rigid body).
    """

    @property
    def physics(self) -> Physics: ...

