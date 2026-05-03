from .volume_field_base import VolumeFieldBase
from ..common import SchemaKind


class FieldBase(VolumeFieldBase):
    """
        \\deprecated This schema will be removed in a future release.
        References to this schema should be updated to refer to VolumeFieldBase.
        """
    schema_kind: SchemaKind = SchemaKind.AbstractTyped
