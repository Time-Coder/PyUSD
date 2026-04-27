from .point_based import PointBased
from ..attribute import Attribute
from ..dtypes import int64
from typing import List


class Points(PointBased):
    """Points are analogous to the <A HREF="https://renderman.pixar.com/resources/RenderMan_20/appnote.18.html">RiPoints spec</A>.  
    
    Points can be an efficient means of storing and rendering particle
    effects comprised of thousands or millions of small particles.  Points
    generally receive a single shading sample each, which should take 
    \\em normals into account, if present.

    While not technically UsdGeomPrimvars, the widths and normals also
    have interpolation metadata.  It's common for authored widths and normals
    to have constant or varying interpolation."""
    
    abstract: bool = False

    def __init__(self, name:str="")->None:
        PointBased.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraPlugInfo": {
                    "implementsComputeExtent": True
                }
            }
        })

        self.create_prop(Attribute(List[float], "widths", metadata={
            "doc": """Widths are defined as the \\em diameter of the points, in 
                 object space.  'widths' is not a generic Primvar, but
                 the number of elements in this attribute will be determined by
                 its 'interpolation'.  See \\ref SetWidthsInterpolation() .  If
                 'widths' and 'primvars:widths' are both specified, the latter
                 has precedence."""
        }))
        self.create_prop(Attribute(List[int64], "ids", metadata={
            "doc": """Ids are optional; if authored, the ids array should be the same
                 length as the points array, specifying (at each timesample if
                 point identities are changing) the id of each point. The
                 type is signed intentionally, so that clients can encode some
                 binary state on Id'd points without adding a separate 
                 primvar."""
        }))
