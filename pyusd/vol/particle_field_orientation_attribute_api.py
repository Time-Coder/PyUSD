from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..gf import quatf, quath
from ..common import SchemaKind


class ParticleFieldOrientationAttributeAPI(APISchemaBase):
    """A ParticleField related applied schema that provides an
             orientations attribute to define the orientation of the particles.

             Attributes are provided in both `float` and `half` types for some
             easy data footprint affordance, data consumers should prefer
             `float` version if available.

             The length of this attribute is expected to match the length of
             the provided position data. If it is too long it will be truncated
             to the number of particles define by the position data. If it is
             too short it will be ignored.

             If the attribute is ignored or not populated, then a default value
             of no rotation should be applied to the kernel instantiated at each
             particle."""
    schema_kind: SchemaKind = SchemaKind.SingleApplyAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": "None"
        }
    }

    orientations: Attribute[List[quatf]] = Attribute(List[quatf], doc="Quaternion orientation for each particle.")

    orientationsh: Attribute[List[quath]] = Attribute(List[quath],
        doc=
        """Quaternion orientation for each particle. If the float
                precision version is defined it should be preferred.
        """
    )
