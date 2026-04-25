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
    def xformOpOrder(self)->Attribute[List[token]]: ...