from ..prim import Prim
from .xformop import XformOp
from ..attribute import Attribute
from ..dtypes import token
from typing import List


class Xform(Prim):

    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)
        self._props["xformOp"] = XformOp(self)
        self._props["xformOpOrder"] = Attribute(self, None, List[token], "xformOpOrder", uniform=True)
        self._props["xformOpOrder"].value = []
        self._props["xformOpOrder"]._value_state = Attribute.ValueState.Fallback