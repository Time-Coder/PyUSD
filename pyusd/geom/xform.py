from ..common import SchemaKind
from .xformable import Xformable


class Xform(Xformable):
    "Concrete prim schema for a transform, which implements Xformable "

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped
