from .point_based import PointBased
from ..attribute import Attribute
from typing import List


class Curves(PointBased):
    """Base class for UsdGeomBasisCurves, UsdGeomNurbsCurves, and
    UsdGeomHermiteCurves.  The BasisCurves schema is designed to be
    analagous to offline renderers' notion of batched curves (such as
    the classical RIB definition via Basis and Curves statements),
    while the NurbsCurve schema is designed to be analgous to the
    NURBS curves found in packages like Maya and Houdini while
    retaining their consistency with the RenderMan specification for
    NURBS Patches. HermiteCurves are useful for the
    interchange of animation guides and paths.

    It is safe to use the length of the curve vertex count to derive
    the number of curves and the number and layout of curve vertices,
    but this schema should NOT be used to derive the number of curve
    points. While vertex indices are implicit in all shipped
    descendent types of this schema, one should not assume that all
    internal or future shipped schemas will follow this pattern. Be
    sure to key any indexing behavior off the concrete type, not this
    abstract type.
    """

    def __init__(self, name:str="")->None: ...

    @property
    def curveVertexCounts(self)->Attribute[List[int]]:
        """Curves-derived primitives can represent multiple distinct,
        potentially disconnected curves.  The length of 'curveVertexCounts'
        gives the number of such curves, and each element describes the
        number of vertices in the corresponding curve"""

    @curveVertexCounts.setter
    def curveVertexCounts(self, value:List[int])->None: ...

    @property
    def widths(self)->Attribute[List[float]]:
        """Provides width specification for the curves, whose application
        will depend on whether the curve is oriented (normals are defined for
        it), in which case widths are "ribbon width", or unoriented, in which
        case widths are cylinder width.  'widths' is not a generic Primvar,
        but the number of elements in this attribute will be determined by
        its 'interpolation'.  See \\ref SetWidthsInterpolation() .  If 'widths'
        and 'primvars:widths' are both specified, the latter has precedence."""

    @widths.setter
    def widths(self, value:List[float])->None: ...
