from .curves import Curves
from ..attribute import Attribute
from ..dtypes import double
from ..gf import double2
from ..common import SchemaKind
from typing import List


class NurbsCurves(Curves):
    """This schema is analagous to NURBS Curves in packages like Maya
    and Houdini, often used for interchange of rigging and modeling curves.  
    Unlike Maya, this curve spec supports batching of multiple curves into a 
    single prim, widths, and normals in the schema.  Additionally, we require 
    'numSegments + 2 * degree + 1' knots (2 more than maya does).  This is to
    be more consistent with RenderMan's NURBS patch specification.  
    
    To express a periodic curve:
    - knot[0] = knot[1] - (knots[-2] - knots[-3]; 
    - knot[-1] = knot[-2] + (knot[2] - knots[1]);
    
    To express a nonperiodic curve:
    - knot[0] = knot[1];
    - knot[-1] = knot[-2];
    
    In spite of these slight differences in the spec, curves generated in Maya
    should be preserved when roundtripping.
    
    \\em order and \\em range, when representing a batched NurbsCurve should be
    authored one value per curve.  \\em knots should be the concatentation of
    all batched curves."""

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    order: Attribute[List[int]] = Attribute(List[int], value=[], doc=
        """Order of the curve.  Order must be positive and is
        equal to the degree of the polynomial basis to be evaluated, plus 1.
        Its value for the 'i'th curve must be less than or equal to
        curveVertexCount[i]"""
    )

    knots: Attribute[List[double]] = Attribute(List[double], "knots", doc=
        """Knot vector providing curve parameterization.
        The length of the slice of the array for the ith curve 
        must be ( curveVertexCount[i] + order[i] ), and its
        entries must take on monotonically increasing values."""
    )

    ranges: Attribute[List[double2]] = Attribute(List[double2], "ranges", doc=
        """Provides the minimum and maximum parametric values (as defined
        by knots) over which the curve is actually defined.  The minimum must 
        be less than the maximum, and greater than or equal to the value of the 
        knots['i'th curve slice][order[i]-1]. The maxium must be less 
        than or equal to the last element's value in knots['i'th curve slice].
        Range maps to (vmin, vmax) in the RenderMan spec."""
    )

    pointWeights: Attribute[List[double]] = Attribute(List[double], "pointWeights", doc=
        """Optionally provides "w" components for each control point,
        thus must be the same length as the points attribute.  If authored,
        the curve will be rational.  If unauthored, the curve will be
        polynomial, i.e. weight for all points is 1.0.
        \\note Some DCC's pre-weight the \\em points, but in this schema, 
        \\em points are not pre-weighted."""
    )
