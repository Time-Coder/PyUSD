from ..common import SchemaKind
from .volume_field_asset import VolumeFieldAsset


class FieldAsset(VolumeFieldAsset):
    """
    \\deprecated This schema will be removed in a future release.
    References to this schema should be updated to refer to VolumeFieldAsset.

    """

    schema_kind: SchemaKind = SchemaKind.AbstractTyped
