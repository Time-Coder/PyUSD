from typing import List

from ..attribute_spec import AttributeSpec
from ..dtypes import double, token
from ..gf import double2
from .point_based import PointBased
from .trim_curve import TrimCurve

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


    class UForm(token):
        Open = "open"
        Closed = "closed"
        Periodic = "periodic"

    class VForm(token):
        Open = "open"
        Closed = "closed"
        Periodic = "periodic"

    @property
    def trimCurve(self) -> TrimCurve: ...

    @property
    def uVertexCount(self)->AttributeSpec[int]:
        """Number of vertices in the U direction.  Should be at least as
        large as uOrder."""

    @uVertexCount.setter
    def uVertexCount(self, value:int)->None: ...

    @property
    def vVertexCount(self)->AttributeSpec[int]:
        """Number of vertices in the V direction.  Should be at least as
        large as vOrder."""

    @vVertexCount.setter
    def vVertexCount(self, value:int)->None: ...

    @property
    def uOrder(self)->AttributeSpec[int]:
        """Order in the U direction.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1."""

    @uOrder.setter
    def uOrder(self, value:int)->None: ...

    @property
    def vOrder(self)->AttributeSpec[int]:
        """Order in the V direction.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1."""

    @vOrder.setter
    def vOrder(self, value:int)->None: ...

    @property
    def uKnots(self)->AttributeSpec[List[double]]:
        """Knot vector for U direction providing U parameterization.
        The length of this array must be ( uVertexCount + uOrder ), and its
        entries must take on monotonically increasing values."""

    @uKnots.setter
    def uKnots(self, value:List[double])->None: ...

    @property
    def vKnots(self)->AttributeSpec[List[double]]:
        """Knot vector for V direction providing U parameterization.
        The length of this array must be ( vVertexCount + vOrder ), and its
        entries must take on monotonically increasing values."""

    @vKnots.setter
    def vKnots(self, value:List[double])->None: ...

    @property
    def uForm(self)->AttributeSpec[UForm]:
        """Interpret the control grid and knot vectors as representing
        an open, geometrically closed, or geometrically closed and C2 continuous
        surface along the U dimension.
        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" """

    @uForm.setter
    def uForm(self, value:UForm)->None: ...

    @property
    def vForm(self)->AttributeSpec[VForm]:
        """Interpret the control grid and knot vectors as representing
        an open, geometrically closed, or geometrically closed and C2 continuous
        surface along the V dimension.
        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" """

    @vForm.setter
    def vForm(self, value:VForm)->None: ...

    @property
    def uRange(self)->AttributeSpec[double2]:
        """Provides the minimum and maximum parametric values (as defined
        by uKnots) over which the surface is actually defined.  The minimum
        must be less than the maximum, and greater than or equal to the
        value of uKnots[uOrder-1].  The maxium must be less than or equal
        to the last element's value in uKnots."""

    @uRange.setter
    def uRange(self, value:double2)->None: ...

    @property
    def vRange(self)->AttributeSpec[double2]:
        """Provides the minimum and maximum parametric values (as defined
        by vKnots) over which the surface is actually defined.  The minimum
        must be less than the maximum, and greater than or equal to the
        value of vKnots[vOrder-1].  The maxium must be less than or equal
        to the last element's value in vKnots."""

    @vRange.setter
    def vRange(self, value:double2)->None: ...

    @property
    def pointWeights(self)->AttributeSpec[List[double]]:
        """Optionally provides "w" components for each control point,
        thus must be the same length as the points attribute.  If authored,
        the patch will be rational.  If unauthored, the patch will be
        polynomial, i.e. weight for all points is 1.0.
        \\note Some DCC's pre-weight the \\em points, but in this schema,
        \\em points are not pre-weighted."""

    @pointWeights.setter
    def pointWeights(self, value:List[double])->None: ...
