from ..prim import Prim
from .xformop import XformOp


class Xform(Prim):

    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)
        self._props["xformOp"] = XformOp()
