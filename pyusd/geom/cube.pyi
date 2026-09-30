from ..attribute import Attribute
from ..dtypes import double
from .mesh import Mesh

class Cube(Mesh):

    def __init__(self, name:str="")->None: ...

    @property
    def size(self) -> Attribute[double]:
        """Indicates the length of each edge of the cube.  If you
        author \\em size you must also author \\em extent.

        \\sa GetExtentAttr()"""

    @size.setter
    def size(self, value:float) -> None: ...
