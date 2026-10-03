from ..attribute_spec import AttributeSpec
from ..dtypes import token

class Outputs(AttributeSpec):

    @property
    def surface(self)->AttributeSpec[token]:
        ...

    @surface.setter
    def surface(self, value:token)->None: ...

    @property
    def displacement(self)->AttributeSpec[token]:
        ...

    @displacement.setter
    def displacement(self, value:token)->None: ...

    @property
    def volume(self)->AttributeSpec[token]:
        ...

    @volume.setter
    def volume(self, value:token)->None: ...
