from ..prim import Prim
from .xformop import XformOp


class Xform(Prim):

    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)

        self._prop_names.append("xformOp")
        self._xformOp:XformOp = XformOp()

    @property
    def xformOp(self)->XformOp:
        return self._xformOp