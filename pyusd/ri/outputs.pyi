from ..attribute import Attribute
from ..dtypes import token

class Outputs(Attribute):

    @property
    def surface(self)->Attribute[token]:
        ...

    @surface.setter
    def surface(self, value:token)->None: ...

    @property
    def displacement(self)->Attribute[token]:
        ...

    @displacement.setter
    def displacement(self, value:token)->None: ...

    @property
    def volume(self)->Attribute[token]:
        ...

    @volume.setter
    def volume(self, value:token)->None: ...
