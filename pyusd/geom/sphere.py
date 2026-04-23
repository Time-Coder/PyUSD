from .mesh import Mesh
from ..attribute import Attribute
from ..dtypes import double


class Sphere(Mesh):
    
    def __init__(self, name:str="")->None:
        Mesh.__init__(self, name)
        self._add_prop(Attribute(double, "radius", value=1.0))
