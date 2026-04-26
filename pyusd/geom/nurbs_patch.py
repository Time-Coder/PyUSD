from .point_base import PointBased
from ..attribute import Attribute
from ..dtypes import namespace, token
from ..gf import double2, double3
from typing import List


class NurbsPatch(PointBased):
    'Encodes a rational or polynomial non-uniform B-spline\n    surface, with optional trim curves.\n    \n    The encoding mostly follows that of RiNuPatch and RiTrimCurve: \n    https://renderman.pixar.com/resources/RenderMan_20/geometricPrimitives.html#rinupatch , with some minor renaming and coalescing for clarity.\n    \n    The layout of control vertices in the \\em points attribute inherited\n    from UsdGeomPointBased is row-major with U considered rows, and V columns.\n    \n    \\anchor UsdGeom_NurbsPatch_Form\n    <b>NurbsPatch Form</b>\n    \n    The authored points, orders, knots, weights, and ranges are all that is\n    required to render the nurbs patch.  However, the only way to model closed\n    surfaces with nurbs is to ensure that the first and last control points\n    along the given axis are coincident.  Similarly, to ensure the surface is\n    not only closed but also C2 continuous, the last \\em order - 1 control\n    points must be (correspondingly) coincident with the first \\em order - 1\n    control points, and also the spacing of the last corresponding knots\n    must be the same as the first corresponding knots.\n    \n    <b>Form</b> is provided as an aid to interchange between modeling and\n    animation applications so that they can robustly identify the intent with\n    which the surface was modelled, and take measures (if they are able) to\n    preserve the continuity/concidence constraints as the surface may be rigged\n    or deformed.  \n    \\li An \\em open-form NurbsPatch has no continuity constraints.\n    \\li A \\em closed-form NurbsPatch expects the first and last control points\n    to overlap\n    \\li A \\em periodic-form NurbsPatch expects the first and last\n    \\em order - 1 control points to overlap.\n    \n    <b>Nurbs vs Subdivision Surfaces</b>\n    \n    Nurbs are an important modeling primitive in CAD/CAM tools and early\n    computer graphics DCC\'s.  Because they have a natural UV parameterization\n    they easily support "trim curves", which allow smooth shapes to be\n    carved out of the surface.\n    \n    However, the topology of the patch is always rectangular, and joining two \n    nurbs patches together (especially when they have differing numbers of\n    spans) is difficult to do smoothly.  Also, nurbs are not supported by\n    the Ptex texturing technology (http://ptex.us).\n    \n    Neither of these limitations are shared by subdivision surfaces; therefore,\n    although they do not subscribe to trim-curve-based shaping, subdivs are\n    often considered a more flexible modeling primitive.\n    '
    abstract: bool = False

    def __init__(self, name:str="")->None:
        PointBased.__init__(self, name)

        self.create_prop(Attribute(int, "uVertexCount", metadata={"doc": "Number of control vertices along the U dimension."}))
        self.create_prop(Attribute(int, "vVertexCount", metadata={"doc": "Number of control vertices along the V dimension."}))
        self.create_prop(Attribute(int, "uOrder", metadata={"doc": "The order of the spline basis in U."}))
        self.create_prop(Attribute(int, "vOrder", metadata={"doc": "The order of the spline basis in V."}))
        self.create_prop(Attribute(List[float], "uKnots", metadata={"doc": "Knot vector for the U dimension."}))
        self.create_prop(Attribute(List[float], "vKnots", metadata={"doc": "Knot vector for the V dimension."}))
        self.create_prop(Attribute(token, "uForm", value="open", uniform=True, metadata={
            "allowedTokens": ["open", "closed", "periodic"],
            "doc": """Describes whether the surface is open, closed, or periodic in U."""
        }))
        self.create_prop(Attribute(token, "vForm", value="open", uniform=True, metadata={
            "allowedTokens": ["open", "closed", "periodic"],
            "doc": """Describes whether the surface is open, closed, or periodic in V."""
        }))
        self.create_prop(Attribute(double2, "uRange", metadata={"doc": "Parametric range over which the surface is defined in U."}))
        self.create_prop(Attribute(double2, "vRange", metadata={"doc": "Parametric range over which the surface is defined in V."}))
        self.create_prop(Attribute(List[float], "pointWeights", metadata={"doc": "Optional control point weights for rational patches."}))

        trim_curve = Attribute(namespace, "trimCurve", is_leaf=False)
        trim_curve.create_prop(Attribute(List[int], "counts", metadata={"doc": "Number of trim loops in each trim curve set."}))
        trim_curve.create_prop(Attribute(List[int], "orders", metadata={"doc": "Order of each trim curve."}))
        trim_curve.create_prop(Attribute(List[int], "vertexCounts", metadata={"doc": "Control vertex count for each trim curve."}))
        trim_curve.create_prop(Attribute(List[float], "knots", metadata={"doc": "Concatenated knot vectors for all trim curves."}))
        trim_curve.create_prop(Attribute(List[double2], "ranges", metadata={"doc": "Parametric ranges for each trim curve."}))
        trim_curve.create_prop(Attribute(List[double3], "points", metadata={"doc": "Homogeneous control points for all trim curves."}))
        self.create_prop(trim_curve)
        # DOCSYNC-BEGIN NurbsPatch
        self.uVertexCount.metadata.update({"doc": 'Number of vertices in the U direction.  Should be at least as\n        large as uOrder.'})
        self.vVertexCount.metadata.update({"doc": 'Number of vertices in the V direction.  Should be at least as\n        large as vOrder.'})
        self.uOrder.metadata.update({"doc": 'Order in the U direction.  Order must be positive and is\n        equal to the degree of the polynomial basis to be evaluated, plus 1.'})
        self.vOrder.metadata.update({"doc": 'Order in the V direction.  Order must be positive and is\n        equal to the degree of the polynomial basis to be evaluated, plus 1.'})
        self.uKnots.metadata.update({"doc": 'Knot vector for U direction providing U parameterization.\n        The length of this array must be ( uVertexCount + uOrder ), and its\n        entries must take on monotonically increasing values.'})
        self.vKnots.metadata.update({"doc": 'Knot vector for V direction providing U parameterization.\n        The length of this array must be ( vVertexCount + vOrder ), and its\n        entries must take on monotonically increasing values.'})
        self.uForm.metadata.update({"doc": 'Interpret the control grid and knot vectors as representing\n        an open, geometrically closed, or geometrically closed and C2 continuous\n        surface along the U dimension.\n        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" '})
        self.vForm.metadata.update({"doc": 'Interpret the control grid and knot vectors as representing\n        an open, geometrically closed, or geometrically closed and C2 continuous\n        surface along the V dimension.\n        \\sa \\ref UsdGeom_NurbsPatch_Form "NurbsPatch Form" '})
        self.uRange.metadata.update({"doc": "Provides the minimum and maximum parametric values (as defined\n        by uKnots) over which the surface is actually defined.  The minimum\n        must be less than the maximum, and greater than or equal to the\n        value of uKnots[uOrder-1].  The maxium must be less than or equal\n        to the last element's value in uKnots."})
        self.vRange.metadata.update({"doc": "Provides the minimum and maximum parametric values (as defined\n        by vKnots) over which the surface is actually defined.  The minimum\n        must be less than the maximum, and greater than or equal to the\n        value of vKnots[vOrder-1].  The maxium must be less than or equal\n        to the last element's value in vKnots."})
        self.pointWeights.metadata.update({"doc": 'Optionally provides "w" components for each control point,\n        thus must be the same length as the points attribute.  If authored,\n        the patch will be rational.  If unauthored, the patch will be\n        polynomial, i.e. weight for all points is 1.0.\n        \\note Some DCC\'s pre-weight the \\em points, but in this schema, \n        \\em points are not pre-weighted.'})
        self.trimCurve.counts.metadata.update({"doc": 'Each element specifies how many curves are present in each\n        "loop" of the trimCurve, and the length of the array determines how\n        many loops the trimCurve contains.  The sum of all elements is the\n        total nuber of curves in the trim, to which we will refer as \n        \\em nCurves in describing the other trim attributes.'})
        self.trimCurve.orders.metadata.update({"doc": 'Flat list of orders for each of the \\em nCurves curves.'})
        self.trimCurve.vertexCounts.metadata.update({"doc": 'Flat list of number of vertices for each of the\n         \\em nCurves curves.'})
        self.trimCurve.knots.metadata.update({"doc": 'Flat list of parametric values for each of the\n        \\em nCurves curves.  There will be as many knots as the sum over\n        all elements of \\em vertexCounts plus the sum over all elements of\n        \\em orders.'})
        self.trimCurve.ranges.metadata.update({"doc": 'Flat list of minimum and maximum parametric values \n        (as defined by \\em knots) for each of the \\em nCurves curves.'})
        self.trimCurve.points.metadata.update({"doc": 'Flat list of homogeneous 2D points (u, v, w) that comprise\n        the \\em nCurves curves.  The number of points should be equal to the\n        um over all elements of \\em vertexCounts.'})
        # DOCSYNC-END NurbsPatch
