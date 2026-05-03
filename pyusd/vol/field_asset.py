from .volume_field_asset import VolumeFieldAsset
from ..common import SchemaKind


class FieldAsset(VolumeFieldAsset):
    """
        \\deprecated This schema will be removed in a future release.
        References to this schema should be updated to refer to VolumeFieldAsset.
        """
    schema_kind: SchemaKind = SchemaKind.AbstractTyped
