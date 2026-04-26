from .point_base import PointBased
from ..attribute import Attribute
from ..gf import double2, double3
from typing import List


class TrimCurve(Attribute):

    @property
    def counts(self)->Attribute[List[int]]:
        """Number of trim loops in each trim curve set."""

    @counts.setter
    def counts(self, value:List[int])->None: ...

    @property
    def orders(self)->Attribute[List[int]]:
        """Order of each trim curve."""

    @orders.setter
    def orders(self, value:List[int])->None: ...

    @property
    def vertexCounts(self)->Attribute[List[int]]:
        """Control vertex count for each trim curve."""

    @vertexCounts.setter
    def vertexCounts(self, value:List[int])->None: ...

    @property
    def knots(self)->Attribute[List[float]]:
        """Concatenated knot vectors for all trim curves."""

    @knots.setter
    def knots(self, value:List[float])->None: ...

    @property
    def ranges(self)->Attribute[List[double2]]:
        """Parametric ranges for each trim curve."""

    @ranges.setter
    def ranges(self, value:List[double2])->None: ...

    @property
    def points(self)->Attribute[List[double3]]:
        """Homogeneous control points for all trim curves."""

    @points.setter
    def points(self, value:List[double3])->None: ...


class NurbsPatch(PointBased):
    'Encodes a rational or polynomial non-uniform B-spline\n    surface, with optional trim curves.\n    \n    The encoding mostly follows that of RiNuPatch and RiTrimCurve: \n    https://renderman.pixar.com/resources/RenderMan_20/geometricPrimitives.html#rinupatch , with some minor renaming and coalescing for clarity.\n    \n    The layout of control vertices in the \\em points attribute inherited\n    from UsdGeomPointBased is row-major with U considered rows, and V columns.\n    \n    \\anchor UsdGeom_NurbsPatch_Form\n    <b>NurbsPatch Form</b>\n    \n    The authored points, orders, knots, weights, and ranges are all that is\n    required to render the nurbs patch.  However, the only way to model closed\n    surfaces with nurbs is to ensure that the first and last control points\n    along the given axis are coincident.  Similarly, to ensure the surface is\n    not only closed but also C2 continuous, the last \\em order - 1 control\n    points must be (correspondingly) coincident with the first \\em order - 1\n    control points, and also the spacing of the last corresponding knots\n    must be the same as the first corresponding knots.\n    \n    <b>Form</b> is provided as an aid to interchange between modeling and\n    animation applications so that they can robustly identify the intent with\n    which the surface was modelled, and take measures (if they are able) to\n    preserve the continuity/concidence constraints as the surface may be rigged\n    or deformed.  \n    \\li An \\em open-form NurbsPatch has no continuity constraints.\n    \\li A \\em closed-form NurbsPatch expects the first and last control points\n    to overlap\n    \\li A \\em periodic-form NurbsPatch expects the first and last\n    \\em order - 1 control points to overlap.\n    \n    <b>Nurbs vs Subdivision Surfaces</b>\n    \n    Nurbs are an important modeling primitive in CAD/CAM tools and early\n    computer graphics DCC\'s.  Because they have a natural UV parameterization\n    they easily support "trim curves", which allow smooth shapes to be\n    carved out of the surface.\n    \n    However, the topology of the patch is always rectangular, and joining two \n    nurbs patches together (especially when they have differing numbers of\n    spans) is difficult to do smoothly.  Also, nurbs are not supported by\n    the Ptex texturing technology (http://ptex.us).\n    \n    Neither of these limitations are shared by subdivision surfaces; therefore,\n    although they do not subscribe to trim-curve-based shaping, subdivs are\n    often considered a more flexible modeling primitive.\n    '
    def __init__(self, name:str="")->None: ...

    @property
    def uVertexCount(self)->Attribute[int]:
        'Number of vertices in the U direction.  Should be at least as\n        large as uOrder.'


    @uVertexCount.setter
    def uVertexCount(self, value:int)->None: ...

    @property
    def vVertexCount(self)->Attribute[int]:
        'Number of vertices in the V direction.  Should be at least as\n        large as vOrder.'


    @vVertexCount.setter
    def vVertexCount(self, value:int)->None: ...

    @property
    def uOrder(self)->Attribute[int]:
        'Order in the U direction.  Order must be positive and is\n        equal to the degree of the polynomial basis to be evaluated, plus 1.'


    @uOrder.setter
    def uOrder(self, value:int)->None: ...

    @property
    def vOrder(self)->Attribute[int]:
        'Order in the V direction.  Order must be positive and is\n        equal to the degree of the polynomial basis to be evaluated, plus 1.'


    @vOrder.setter
    def vOrder(self, value:int)->None: ...

    @property
    def uKnots(self)->Attribute[List[float]]:
        'Knot vector for U direction providing U parameterization.\n        The length of this array must be ( uVertexCount + uOrder ), and its\n        entries must take on monotonically increasing values.'


    @uKnots.setter
    def uKnots(self, value:List[float])->None: ...

    @property
    def vKnots(self)->Attribute[List[float]]:
        'Knot vector for V direction providing U parameterization.\n        The length of this array must be ( vVertexCount + vOrder ), and its\n        entries must take on monotonically increasing values.'


    @vKnots.setter
    def vKnots(self, value:List[float])->None: ...

    @property
    def uForm(self)->Attribute[str]:
        'Interpret the control grid and knot vectors as representing\n        an open, geometrically closed, or geometrically closed and C2 continuous\n        surface along the U dimension.\n        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" '


    @uForm.setter
    def uForm(self, value:str)->None: ...

    @property
    def vForm(self)->Attribute[str]:
        'Interpret the control grid and knot vectors as representing\n        an open, geometrically closed, or geometrically closed and C2 continuous\n        surface along the V dimension.\n        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" '


    @vForm.setter
    def vForm(self, value:str)->None: ...

    @property
    def uRange(self)->Attribute[double2]:
        "Provides the minimum and maximum parametric values (as defined\n        by uKnots) over which the surface is actually defined.  The minimum\n        must be less than the maximum, and greater than or equal to the\n        value of uKnots[uOrder-1].  The maxium must be less than or equal\n        to the last element's value in uKnots."


    @uRange.setter
    def uRange(self, value:double2)->None: ...

    @property
    def vRange(self)->Attribute[double2]:
        "Provides the minimum and maximum parametric values (as defined\n        by vKnots) over which the surface is actually defined.  The minimum\n        must be less than the maximum, and greater than or equal to the\n        value of vKnots[vOrder-1].  The maxium must be less than or equal\n        to the last element's value in vKnots."


    @vRange.setter
    def vRange(self, value:double2)->None: ...

    @property
    def pointWeights(self)->Attribute[List[float]]:
        'Optionally provides "w" components for each control point,\n        thus must be the same length as the points attribute.  If authored,\n        the patch will be rational.  If unauthored, the patch will be\n        polynomial, i.e. weight for all points is 1.0.\n        \\note Some DCC\'s pre-weight the \\em points, but in this schema, \n        \\em points are not pre-weighted.'


    @pointWeights.setter
    def pointWeights(self, value:List[float])->None: ...

    @property
    def trimCurve(self)->TrimCurve:
        """Namespace containing trim curve data for the patch."""
