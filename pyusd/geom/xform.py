from ..prim import Prim
from .xformop import XformOp
from ..attribute import Attribute
from ..dtypes import token
from typing import List


class Xform(Prim):

    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)
        self._add_prop(XformOp())
        self._add_prop(Attribute(List[token], "xformOpOrder", value=[], uniform=True))
