from ..attribute import Attribute

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
