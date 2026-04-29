from .xformable import Xformable
from ..common import SchemaKind


class Xform(Xformable):
    """Concrete prim schema for a transform, which implements Xformable """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    def __init__(self, name:str="")->None:
        Xformable.__init__(self, name)
        