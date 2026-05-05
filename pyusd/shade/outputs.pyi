from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from typing import List


class Outputs(Attribute):

    @property
    def surface(self)->Attribute[token]:
        """Represents the universal "surface" output terminal of a
        material."""

    @surface.setter
    def surface(self, value:token)->None: ...

    @property
    def displacement(self)->Attribute[token]:
        """Represents the universal "displacement" output terminal of a 
        material."""

    @displacement.setter
    def displacement(self, value:token)->None: ...

    @property
    def volume(self)->Attribute[token]:
        """Represents the universal "volume" output terminal of a
        material."""

    @volume.setter
    def volume(self, value:token)->None: ...
