from pyusd.geom.xformable import Xformable
from ..common import SchemaKind


class VolumeFieldBase(Xformable):
    """Base class for volume field primitives."""
    schema_kind: SchemaKind = SchemaKind.AbstractTyped
