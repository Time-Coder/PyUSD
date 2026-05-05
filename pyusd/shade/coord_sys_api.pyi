from ..api_schema_base import APISchemaBase
from .info import Info
from .outputs import Outputs


class CoordSysAPI(APISchemaBase):
    """UsdShadeCoordSysAPI provides a way to designate, name,
    and discover coordinate systems.
    
    Coordinate systems are implicitly established by UsdGeomXformable
    prims, using their local space.  That coordinate system may be
    bound (i.e., named) from another prim.  The binding is encoded
    as a single-target relationship.
    Coordinate system bindings apply to descendants of the prim
    where the binding is expressed, but names may be re-bound by
    descendant prims.
    
    CoordSysAPI is a multi-apply API schema, where instance names 
    signify the named coordinate systems. The instance names are
    used with the "coordSys:" namespace to determine the binding
    to the UsdGeomXformable prim.
    
    Named coordinate systems are useful in shading (and other) workflows.
    An example is projection paint, which projects a texture
    from a certain view (the paint coordinate system), encoded as 
    (e.g.) "rel coordSys:paint:binding".  Using the paint coordinate frame 
    avoids the need to assign a UV set to the object, and can be a 
    concise way to project paint across a collection of objects with 
    a single shared paint coordinate system.
    
    """

    @property
    def binding(self)->Relationship:
        """Prim binding expressing the appropriate coordinate systems."""

    @binding.setter
    def binding(self, value:Relationship)->None: ...

