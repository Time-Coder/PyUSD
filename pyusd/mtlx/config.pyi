from ..attribute import Attribute
from ..dtypes import string

class Config(Attribute):

    @property
    def version(self)->Attribute[string]:
        """MaterialX library version that the data has been authored
        against. Defaults to 1.38 to allow correct verisoning of old files."""

    @version.setter
    def version(self, value:string)->None: ...
