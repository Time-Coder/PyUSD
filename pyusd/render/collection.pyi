from ..attribute import Attribute
from typing import List


class Collection(Attribute):

    @property
    def includeRoot(self)->Attribute[bool]:
        ...

    @includeRoot.setter
    def includeRoot(self, value:bool)->None: ...

    @property
    def includeRoot(self)->Attribute[bool]:
        ...

    @includeRoot.setter
    def includeRoot(self, value:bool)->None: ...
