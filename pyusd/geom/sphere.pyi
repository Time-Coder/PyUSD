from ..prim import Prim
from ..attribute import Attribute


class Sphere(Prim):
    
    def __init__(self, name:str="")->None: ...

    @property
    def radius(self) -> Attribute: ...

    @radius.setter
    def radius(self, value:float) -> None: ...