from ..prim import Prim
from ..attribute import Attribute
from ..dtypes import double


class Sphere(Prim):
    
    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)
        self._props["radius"] = Attribute(double, "radius")
