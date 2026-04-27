from .point_based import PointBased
from ..attribute import Attribute
from ..gf import double2, double3
from typing import List


class TrimCurve(Attribute):

    @property
    def counts(self)->Attribute[List[int]]:
        """Each element specifies how many curves are present in each
        "loop" of the trimCurve, and the length of the array determines how
        many loops the trimCurve contains.  The sum of all elements is the
        total nuber of curves in the trim, to which we will refer as 
        \\em nCurves in describing the other trim attributes."""

    @counts.setter
    def counts(self, value:List[int])->None: ...

    @property
    def orders(self)->Attribute[List[int]]:
        """Flat list of orders for each of the \\em nCurves curves."""

    @orders.setter
    def orders(self, value:List[int])->None: ...

    @property
    def vertexCounts(self)->Attribute[List[int]]:
        """Flat list of number of vertices for each of the
         \\em nCurves curves."""

    @vertexCounts.setter
    def vertexCounts(self, value:List[int])->None: ...

    @property
    def knots(self)->Attribute[List[float]]:
        """Flat list of parametric values for each of the
        \\em nCurves curves.  There will be as many knots as the sum over
        all elements of \\em vertexCounts plus the sum over all elements of
        \\em orders."""

    @knots.setter
    def knots(self, value:List[float])->None: ...

    @property
    def ranges(self)->Attribute[List[double2]]:
        """Flat list of minimum and maximum parametric values 
        (as defined by \\em knots) for each of the \\em nCurves curves."""

    @ranges.setter
    def ranges(self, value:List[double2])->None: ...

    @property
    def points(self)->Attribute[List[double3]]:
        """Flat list of homogeneous 2D points (u, v, w) that comprise
        the \\em nCurves curves.  The number of points should be equal to the
        um over all elements of \\em vertexCounts."""

    @points.setter
    def points(self, value:List[double3])->None: ...


class NurbsPatch(PointBased):
    """Encodes a rational or polynomial non-uniform B-spline
    surface, with optional trim curves.
    
    The encoding mostly follows that of RiNuPatch and RiTrimCurve: 
    https://renderman.pixar.com/resources/RenderMan_20/geometricPrimitives.html#rinupatch , with some minor renaming and coalescing for clarity.
    
    The layout of control vertices in the \\em points attribute inherited
    from UsdGeomPointBased is row-major with U considered rows, and V columns.
    
    \\anchor UsdGeom_NurbsPatch_Form
    <b>NurbsPatch Form</b>
    
    The authored points, orders, knots, weights, and ranges are all that is
    required to render the nurbs patch.  However, the only way to model closed
    surfaces with nurbs is to ensure that the first and last control points
    along the given axis are coincident.  Similarly, to ensure the surface is
    not only closed but also C2 continuous, the last \\em order - 1 control
    points must be (correspondingly) coincident with the first \\em order - 1
    control points, and also the spacing of the last corresponding knots
    must be the same as the first corresponding knots.
    
    <b>Form</b> is provided as an aid to interchange between modeling and
    animation applications so that they can robustly identify the intent with
    which the surface was modelled, and take measures (if they are able) to
    preserve the continuity/concidence constraints as the surface may be rigged
    or deformed.  
    \\li An \\em open-form NurbsPatch has no continuity constraints.
    \\li A \\em closed-form NurbsPatch expects the first and last control points
    to overlap
    \\li A \\em periodic-form NurbsPatch expects the first and last
    \\em order - 1 control points to overlap.
    
    <b>Nurbs vs Subdivision Surfaces</b>
    
    Nurbs are an important modeling primitive in CAD/CAM tools and early
    computer graphics DCC's.  Because they have a natural UV parameterization
    they easily support "trim curves", which allow smooth shapes to be
    carved out of the surface.
    
    However, the topology of the patch is always rectangular, and joining two 
    nurbs patches together (especially when they have differing numbers of
    spans) is difficult to do smoothly.  Also, nurbs are not supported by
    the Ptex texturing technology (http://ptex.us).
    
    Neither of these limitations are shared by subdivision surfaces; therefore,
    although they do not subscribe to trim-curve-based shaping, subdivs are
    often considered a more flexible modeling primitive.
    """
    
    def __init__(self, name:str="")->None: ...

    @property
    def uVertexCount(self)->Attribute[int]:
        """Number of vertices in the U direction.  Should be at least as
        large as uOrder."""


    @uVertexCount.setter
    def uVertexCount(self, value:int)->None: ...

    @property
    def vVertexCount(self)->Attribute[int]:
        """Number of vertices in the V direction.  Should be at least as
        large as vOrder."""


    @vVertexCount.setter
    def vVertexCount(self, value:int)->None: ...

    @property
    def uOrder(self)->Attribute[int]:
        """Order in the U direction.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1."""


    @uOrder.setter
    def uOrder(self, value:int)->None: ...

    @property
    def vOrder(self)->Attribute[int]:
        """Order in the V direction.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1."""


    @vOrder.setter
    def vOrder(self, value:int)->None: ...

    @property
    def uKnots(self)->Attribute[List[float]]:
        """Knot vector for U direction providing U parameterization.
        The length of this array must be ( uVertexCount + uOrder ), and its
        entries must take on monotonically increasing values."""  


    @uKnots.setter
    def uKnots(self, value:List[float])->None: ...

    @property
    def vKnots(self)->Attribute[List[float]]:
        """Knot vector for V direction providing U parameterization.
        The length of this array must be ( vVertexCount + vOrder ), and its
        entries must take on monotonically increasing values."""  

    @vKnots.setter
    def vKnots(self, value:List[float])->None: ...

    @property
    def uForm(self)->Attribute[str]:
        """Interpret the control grid and knot vectors as representing
        an open, geometrically closed, or geometrically closed and C2 continuous
        surface along the U dimension.
        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" """

    @uForm.setter
    def uForm(self, value:str)->None: ...

    @property
    def vForm(self)->Attribute[str]:
        """Interpret the control grid and knot vectors as representing
        an open, geometrically closed, or geometrically closed and C2 continuous
        surface along the V dimension.
        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" """

    @vForm.setter
    def vForm(self, value:str)->None: ...

    @property
    def uRange(self)->Attribute[double2]:
        """Provides the minimum and maximum parametric values (as defined
        by uKnots) over which the surface is actually defined.  The minimum
        must be less than the maximum, and greater than or equal to the
        value of uKnots[uOrder-1].  The maxium must be less than or equal
        to the last element's value in uKnots."""

    @uRange.setter
    def uRange(self, value:double2)->None: ...

    @property
    def vRange(self)->Attribute[double2]:
        """Provides the minimum and maximum parametric values (as defined
        by vKnots) over which the surface is actually defined.  The minimum
        must be less than the maximum, and greater than or equal to the
        value of vKnots[vOrder-1].  The maxium must be less than or equal
        to the last element's value in vKnots."""

    @vRange.setter
    def vRange(self, value:double2)->None: ...

    @property
    def pointWeights(self)->Attribute[List[float]]:
        """Optionally provides "w" components for each control point,
        thus must be the same length as the points attribute.  If authored,
        the patch will be rational.  If unauthored, the patch will be
        polynomial, i.e. weight for all points is 1.0.
        \\note Some DCC's pre-weight the \\em points, but in this schema, 
        \\em points are not pre-weighted."""

    @pointWeights.setter
    def pointWeights(self, value:List[float])->None: ...

    @property
    def trimCurve(self)->TrimCurve:
        """Namespace containing trim curve data for the patch."""
