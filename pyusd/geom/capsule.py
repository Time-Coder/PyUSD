from .gprim import Gprim
from ..attribute import Attribute
from ..dtypes import double, token
from ..common import SchemaKind
from ..gf import float3
from typing import List


class Capsule(Gprim):
    """Defines a primitive capsule, i.e. a cylinder capped by two half
    spheres, centered at the origin, whose spine is along the specified
    \\em axis.
    The spherical cap heights (sagitta) of the two endcaps are a function of 
    the relative radii of the endcaps, such that cylinder tangent and sphere 
    tangent are coincident and maintain C1 continuity."""
    
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": True
            }
        }
    }

    height: Attribute[double] = Attribute(double, "height", value=1.0, doc=
        """The length of the capsule's spine along the specified
        \\em axis excluding the size of the two half spheres, i.e.
        the length of the cylinder portion of the capsule.
        If you author \\em height you must also author \\em extent.
        \\sa GetExtentAttr()"""
    )
    radius: Attribute[double] = Attribute(double, "radius", value=0.5, doc=
        """The radius of the capsule.  If you
        author \\em radius you must also author \\em extent.
        
        \\sa GetExtentAttr()"""
    )
    axis: Attribute[token] = Attribute(token, "axis", value="Z", uniform=True,
        metadata={
            "allowedTokens": ["X", "Y", "Z"]
        },
        doc = "The axis along which the spine of the capsule is aligned"
    )
    extent: Attribute[List[float3]] = Attribute(List[float3], value=[(-0.5, -0.5, -1.0), (0.5, 0.5, 1.0)], doc=
        """Extent is re-defined on Capsule only to provide a fallback
        value. \\sa UsdGeomGprim::GetExtentAttr()."""
    )
