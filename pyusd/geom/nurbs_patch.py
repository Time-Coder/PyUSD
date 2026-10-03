from typing import List

from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import double, namespace, token
from ..gf import double2, double3
from .point_based import PointBased


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

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    class UForm(token):
        Open = "open"
        Closed = "closed"
        Periodic = "periodic"

    class VForm(token):
        Open = "open"
        Closed = "closed"
        Periodic = "periodic"


    trimCurve: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    trimCurve.counts = AttributeSpec(List[int],
        doc="""Each element specifies how many curves are present in each
        "loop" of the trimCurve, and the length of the array determines how
        many loops the trimCurve contains.  The sum of all elements is the
        total nuber of curves in the trim, to which we will refer as
        \\em nCurves in describing the other trim attributes.
        """
    )
    trimCurve.orders = AttributeSpec(List[int], doc="Flat list of orders for each of the \\em nCurves curves.")
    trimCurve.vertexCounts = AttributeSpec(List[int],
        doc="""Flat list of number of vertices for each of the
        \\em nCurves curves.
        """
    )
    trimCurve.knots = AttributeSpec(List[double],
        doc="""Flat list of parametric values for each of the
        \\em nCurves curves.  There will be as many knots as the sum over
        all elements of \\em vertexCounts plus the sum over all elements of
        \\em orders.
        """
    )
    trimCurve.ranges = AttributeSpec(List[double2],
        doc="""Flat list of minimum and maximum parametric values
        (as defined by \\em knots) for each of the \\em nCurves curves.
        """
    )
    trimCurve.points = AttributeSpec(List[double3],
        doc="""Flat list of homogeneous 2D points (u, v, w) that comprise
        the \\em nCurves curves.  The number of points should be equal to the
        um over all elements of \\em vertexCounts.
        """
    )

    uVertexCount: AttributeSpec[int] = AttributeSpec(int,
        doc="""Number of vertices in the U direction.  Should be at least as
        large as uOrder.
        """
    )

    vVertexCount: AttributeSpec[int] = AttributeSpec(int,
        doc="""Number of vertices in the V direction.  Should be at least as
        large as vOrder.
        """
    )

    uOrder: AttributeSpec[int] = AttributeSpec(int,
        doc="""Order in the U direction.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1.
        """
    )

    vOrder: AttributeSpec[int] = AttributeSpec(int,
        doc="""Order in the V direction.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1.
        """
    )

    uKnots: AttributeSpec[List[double]] = AttributeSpec(List[double],
        value=[],
        doc="""Knot vector for U direction providing U parameterization.
        The length of this array must be ( uVertexCount + uOrder ), and its
        entries must take on monotonically increasing values.
        """
    )

    vKnots: AttributeSpec[List[double]] = AttributeSpec(List[double],
        value=[],
        doc="""Knot vector for V direction providing U parameterization.
        The length of this array must be ( vVertexCount + vOrder ), and its
        entries must take on monotonically increasing values.
        """
    )

    uForm: AttributeSpec[UForm] = AttributeSpec(UForm,
        uniform=True,
        doc="""Interpret the control grid and knot vectors as representing
        an open, geometrically closed, or geometrically closed and C2 continuous
        surface along the U dimension.
        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form"
        """
    )

    vForm: AttributeSpec[VForm] = AttributeSpec(VForm,
        uniform=True,
        doc="""Interpret the control grid and knot vectors as representing
        an open, geometrically closed, or geometrically closed and C2 continuous
        surface along the V dimension.
        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form"
        """
    )

    uRange: AttributeSpec[double2] = AttributeSpec(double2,
        doc="""Provides the minimum and maximum parametric values (as defined
        by uKnots) over which the surface is actually defined.  The minimum
        must be less than the maximum, and greater than or equal to the
        value of uKnots[uOrder-1].  The maxium must be less than or equal
        to the last element's value in uKnots.
        """
    )

    vRange: AttributeSpec[double2] = AttributeSpec(double2,
        doc="""Provides the minimum and maximum parametric values (as defined
        by vKnots) over which the surface is actually defined.  The minimum
        must be less than the maximum, and greater than or equal to the
        value of vKnots[vOrder-1].  The maxium must be less than or equal
        to the last element's value in vKnots.
        """
    )

    pointWeights: AttributeSpec[List[double]] = AttributeSpec(List[double],
        value=[],
        doc="""Optionally provides "w" components for each control point,
        thus must be the same length as the points attribute.  If authored,
        the patch will be rational.  If unauthored, the patch will be
        polynomial, i.e. weight for all points is 1.0.
        \\note Some DCC's pre-weight the \\em points, but in this schema,
        \\em points are not pre-weighted.
        """
    )
