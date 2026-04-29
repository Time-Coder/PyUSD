from .prim import Prim
from .common import SchemaKind


class Typed(Prim):
    """The base class for all \\em typed schemas (those that can impart a
    typeName to a UsdPrim), and therefore the base class for all
    concrete, instantiable "IsA" schemas.
       
    UsdTyped implements a typeName-based query for its override of
    UsdSchemaBase::_IsCompatible().  It provides no other behavior."""

    schema_kind: SchemaKind = SchemaKind.AbstractTyped
