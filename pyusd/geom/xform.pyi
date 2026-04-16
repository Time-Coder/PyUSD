from ..prim import Prim
from .xformop import XformOp


class Xform(Prim):

    def __init__(self, name:str="")->None: ...

    @property
    def xformOp(self)->XformOp: ...