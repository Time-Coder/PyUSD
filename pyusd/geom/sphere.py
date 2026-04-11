from ..prim import Prim
from ..attribute import Attribute
from typeguard import typechecked


class Sphere(Prim):
    
    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)

        self._prop_names.append("radius")
        self._radius:Attribute = Attribute("double", "radius")

    @property
    def radius(self)->Attribute:
        return self._radius
    
    @radius.setter
    @typechecked
    def radius(self, value:float)->None:
        self._radius.value = value