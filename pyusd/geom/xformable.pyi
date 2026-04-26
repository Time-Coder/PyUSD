from .imageable import Imageable
from ..attribute import Attribute
from ..dtypes import token
from .xformop import XformOp
from typing import List


class Xformable(Imageable):

    def __init__(self, name:str="")->None: ...

    @property
    def xformOp(self)->XformOp: ...

    @property
    def xformOpOrder(self)->Attribute[List[token]]:
        """Encodes the sequence of transformation operations in the
        order in which they should be pushed onto a transform stack while
        visiting a UsdStage's prims in a graph traversal that will effect
        the desired positioning for this prim and its descendant prims.
        
        You should rarely, if ever, need to manipulate this attribute directly.
        It is managed by the AddXformOp(), SetResetXformStack(), and
        SetXformOpOrder(), and consulted by GetOrderedXformOps() and
        GetLocalTransformation()."""