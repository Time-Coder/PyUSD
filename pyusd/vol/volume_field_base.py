from ..common import SchemaKind
from ..geom.xformable import Xformable


class VolumeFieldBase(Xformable):
    "Base class for volume field primitives."

    schema_kind: SchemaKind = SchemaKind.AbstractTyped
