from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from typing import List


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
