from ..attribute_spec import AttributeSpec
from ..dtypes import string

class Config(AttributeSpec):

    @property
    def version(self)->AttributeSpec[string]:
        """MaterialX library version that the data has been authored
        against. Defaults to 1.38 to allow correct verisoning of old files."""

    @version.setter
    def version(self, value:string)->None: ...
