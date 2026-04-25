from ..attribute import Attribute
from .boundable import Boundable
from .primvars import PrimVars
from ..dtypes import token


class Gprim(Boundable):
    
    def __init__(self, name:str="")->None: ...

    @property
    def primvars(self) -> PrimVars: ...

    @property
    def doubleSided(self) -> Attribute[bool]: ...

    @doubleSided.setter
    def doubleSided(self, value:bool) -> None: ...

    @property
    def orientation(self) -> Attribute[token]: ...

    @orientation.setter
    def orientation(self, value:token) -> None: ...