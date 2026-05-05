from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class FieldBase(APISchemaBase):
    """
    \\deprecated This schema will be removed in a future release.
    References to this schema should be updated to refer to VolumeFieldBase.
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI
