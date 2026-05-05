from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class VolumeFieldBase(APISchemaBase):
    "Base class for volume field primitives."

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI
