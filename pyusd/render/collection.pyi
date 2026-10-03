from ..attribute_spec import AttributeSpec

class Collection(AttributeSpec):

    @property
    def includeRoot(self)->AttributeSpec[bool]:
        ...

    @includeRoot.setter
    def includeRoot(self, value:bool)->None: ...

    @property
    def includeRoot(self)->AttributeSpec[bool]:
        ...

    @includeRoot.setter
    def includeRoot(self, value:bool)->None: ...
