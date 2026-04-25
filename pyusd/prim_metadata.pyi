from .metadata import Metadata
from .sdf import Specifier


class PrimMetadata(Metadata):
        
    @property
    def specifier(self)->Specifier: ...

    @property
    def typeName(self)->str: ...
