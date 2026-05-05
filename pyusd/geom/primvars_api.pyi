from ..api_schema_base import APISchemaBase
from .exposure import Exposure
from .model import Model
from .motion import Motion
from .primvars import Primvars
from .shutter import Shutter
from .trim_curve import TrimCurve


class PrimvarsAPI(APISchemaBase):
    """UsdGeomPrimvarsAPI encodes geometric "primitive variables",
    as UsdGeomPrimvar, which interpolate across a primitive's topology,
    can override shader inputs, and inherit down namespace.
    
    \\section usdGeom_PrimvarFetchingAPI Which Method to Use to Retrieve Primvars
    
     While creating primvars is unambiguous (CreatePrimvar()), there are quite
     a few methods available for retrieving primvars, making it potentially
     confusing knowing which one to use.  Here are some guidelines:
    
     \\li If you are populating a GUI with the primvars already available for 
     authoring values on a prim, use GetPrimvars().
     \\li If you want all of the "useful" (e.g. to a renderer) primvars
     available at a prim, including those inherited from ancestor prims, use
     FindPrimvarsWithInheritance().  Note that doing so individually for many
     prims will be inefficient.
     \\li To find a particular primvar defined directly on a prim, which may
     or may not provide a value, use GetPrimvar().
     \\li To find a particular primvar defined on a prim or inherited from
     ancestors, which may or may not provide a value, use 
     FindPrimvarWithInheritance().
     \\li To *efficiently* query for primvars using the overloads of
     FindPrimvarWithInheritance() and FindPrimvarsWithInheritance(), one
     must first cache the results of FindIncrementallyInheritablePrimvars() for
     each non-leaf prim on the stage. 
    """

