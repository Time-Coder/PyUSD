from ..prim import Prim
from ..attribute import Attribute
from ..gf import float3
from .xform import Xform
from typing import List


class Mesh(Xform):
    
    def __init__(self, name:str="")->None:
        Xform.__init__(self, name)
        self._add_prop(Attribute(List[float3], "extent"))
