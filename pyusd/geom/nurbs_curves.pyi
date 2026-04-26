from .curves import Curves
from ..attribute import Attribute
from ..gf import double2
from typing import List


class NurbsCurves(Curves):
    "This schema is analagous to NURBS Curves in packages like Maya\n    and Houdini, often used for interchange of rigging and modeling curves.  \n    Unlike Maya, this curve spec supports batching of multiple curves into a \n    single prim, widths, and normals in the schema.  Additionally, we require \n    'numSegments + 2 * degree + 1' knots (2 more than maya does).  This is to\n    be more consistent with RenderMan's NURBS patch specification.  \n    \n    To express a periodic curve:\n    - knot[0] = knot[1] - (knots[-2] - knots[-3]; \n    - knot[-1] = knot[-2] + (knot[2] - knots[1]);\n    \n    To express a nonperiodic curve:\n    - knot[0] = knot[1];\n    - knot[-1] = knot[-2];\n    \n    In spite of these slight differences in the spec, curves generated in Maya\n    should be preserved when roundtripping.\n    \n    \\em order and \\em range, when representing a batched NurbsCurve should be\n    authored one value per curve.  \\em knots should be the concatentation of\n    all batched curves."
    def __init__(self, name:str="")->None: ...

    @property
    def order(self)->Attribute[List[int]]:
        "Order of the curve.  Order must be positive and is\n        equal to the degree of the polynomial basis to be evaluated, plus 1.\n        Its value for the 'i'th curve must be less than or equal to\n        curveVertexCount[i]"


    @order.setter
    def order(self, value:List[int])->None: ...

    @property
    def knots(self)->Attribute[List[float]]:
        'Knot vector providing curve parameterization.\n        The length of the slice of the array for the ith curve \n        must be ( curveVertexCount[i] + order[i] ), and its\n        entries must take on monotonically increasing values.'


    @knots.setter
    def knots(self, value:List[float])->None: ...

    @property
    def ranges(self)->Attribute[List[double2]]:
        "Provides the minimum and maximum parametric values (as defined\n        by knots) over which the curve is actually defined.  The minimum must \n        be less than the maximum, and greater than or equal to the value of the \n        knots['i'th curve slice][order[i]-1]. The maxium must be less \n        than or equal to the last element's value in knots['i'th curve slice].\n\tRange maps to (vmin, vmax) in the RenderMan spec."


    @ranges.setter
    def ranges(self, value:List[double2])->None: ...

    @property
    def pointWeights(self)->Attribute[List[float]]:
        'Optionally provides "w" components for each control point,\n        thus must be the same length as the points attribute.  If authored,\n        the curve will be rational.  If unauthored, the curve will be\n        polynomial, i.e. weight for all points is 1.0.\n        \\note Some DCC\'s pre-weight the \\em points, but in this schema, \n        \\em points are not pre-weighted.'


    @pointWeights.setter
    def pointWeights(self, value:List[float])->None: ...
