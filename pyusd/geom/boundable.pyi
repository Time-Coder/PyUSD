from .xformable import Xformable
from ..attribute import Attribute
from ..gf import float3
from typing import List


class Boundable(Xformable):

    def __init__(self, name:str="")->None: ...

    @property
    def extent(self)->Attribute[List[float3]]:...

    @extent.setter
    def extent(self, value:List[float3])->None: ...