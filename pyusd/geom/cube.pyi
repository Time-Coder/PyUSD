from .mesh import Mesh
from ..attribute import Attribute
from ..dtypes import double


class Cube(Mesh):
    
    def __init__(self, name:str="")->None: ...

    @property
    def size(self) -> Attribute[double]: ...

    @size.setter
    def size(self, value:float) -> None: ...