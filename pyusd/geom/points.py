from .point_base import PointBased
from ..attribute import Attribute
from ..dtypes import int64
from typing import List


class Points(PointBased):
    'Points are analogous to the <A HREF="https://renderman.pixar.com/resources/RenderMan_20/appnote.18.html">RiPoints spec</A>.  \n    \n    Points can be an efficient means of storing and rendering particle\n    effects comprised of thousands or millions of small particles.  Points\n    generally receive a single shading sample each, which should take \n    \\em normals into account, if present.\n\n    While not technically UsdGeomPrimvars, the widths and normals also\n    have interpolation metadata.  It\'s common for authored widths and normals\n    to have constant or varying interpolation.'
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
            "doc": """Per-point widths used when imaging the point cloud."""
        }))
        self.create_prop(Attribute(List[int64], "ids", metadata={
            "doc": """Optional stable identifiers for points over time."""
        }))
        # DOCSYNC-BEGIN Points
        self.widths.metadata.update({"doc": "Widths are defined as the \\em diameter of the points, in \n                 object space.  'widths' is not a generic Primvar, but\n                 the number of elements in this attribute will be determined by\n                 its 'interpolation'.  See \\ref SetWidthsInterpolation() .  If\n                 'widths' and 'primvars:widths' are both specified, the latter\n                 has precedence."})
        self.ids.metadata.update({"doc": "Ids are optional; if authored, the ids array should be the same\n                 length as the points array, specifying (at each timesample if\n                 point identities are changing) the id of each point. The\n                 type is signed intentionally, so that clients can encode some\n                 binary state on Id'd points without adding a separate \n                 primvar."})
        # DOCSYNC-END Points
