from ..common import SchemaKind
from .volume_field_base import VolumeFieldBase


class FieldBase(VolumeFieldBase):
    """
    \\deprecated This schema will be removed in a future release.
    References to this schema should be updated to refer to VolumeFieldBase.

    """

    schema_kind: SchemaKind = SchemaKind.AbstractTyped
