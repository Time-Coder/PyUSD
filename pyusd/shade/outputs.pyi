from ..attribute_spec import AttributeSpec
from ..dtypes import token

class Outputs(AttributeSpec):

    @property
    def surface(self)->AttributeSpec[token]:
        """Represents the universal "surface" output terminal of a
        material."""

    @surface.setter
    def surface(self, value:token)->None: ...

    @property
    def displacement(self)->AttributeSpec[token]:
        """Represents the universal "displacement" output terminal of a
        material."""

    @displacement.setter
    def displacement(self, value:token)->None: ...

    @property
    def volume(self)->AttributeSpec[token]:
        """Represents the universal "volume" output terminal of a
        material."""

    @volume.setter
    def volume(self, value:token)->None: ...
