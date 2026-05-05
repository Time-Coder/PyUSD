from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import double2, double3
from ..dtypes import double
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
    def knots(self)->Attribute[List[double]]:
        """Flat list of parametric values for each of the
        \\em nCurves curves.  There will be as many knots as the sum over
        all elements of \\em vertexCounts plus the sum over all elements of
        \\em orders."""

    @knots.setter
    def knots(self, value:List[double])->None: ...

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
