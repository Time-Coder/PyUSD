from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class ParticleFieldPositionBaseAPI(APISchemaBase):
    """Defines a base-class type applied schema that all applied schema
            that provide the ParticleField position data will automatically apply.
            The purpose of this base class is to allow validation to enforce
            that an applied schema that defines position is always present for a
            ParticleField.

            The number of positions provided is also used to determine the
            number of particle in the ParticleField. If no position data is
            present, then the ParticleField contains no particles. Any other
            per-particle data provided, such as scale or orientation, is
            truncated if too long, or if too short the entire data set will be
            discarded. For these other per-particle data fields, if no data is
            provided, or it is discarded then its default value will be used.
            """
    schema_kind: SchemaKind = SchemaKind.SingleApplyAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply"
        }
    }
