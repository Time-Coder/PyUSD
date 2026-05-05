from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..gf import float3
from ..common import SchemaKind


class ParticleFieldScaleAttributeAPI(APISchemaBase):
    """A ParticleField related applied schema that provides a
    scales attribute to define the linear scale factor applied to the
    particles.
    
    The scales here are linear scales, in line with scales provided
    elsewhere in USD, and not specified in log-format as is sometimes
    seen in PLY files associated with gaussian splats.
    
    Attributes are provided in both `float` and `half` types for some
    easy data footprint affordance, data consumers should prefer
    `float` version if available.
    
    The length of this attribute is expected to match the length of
    the provided position data. If it is too long it will be truncated
    to the number of particles define by the position data. If it is
    too short it will be ignored.
    
    If the attribute is ignored or not provided, then a default unit
    scale should be applied to the kernel.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": None
        }
    }

    scales = Attribute(List[float3],
        doc="""Affine linear scale factor applied to the kernel that is
        instantiated at each particle.
        """
    )

    scalesh = Attribute(List[half3],
        doc="""Affine linear scale factor applied to the kernel that is
        instantiated at each particle. If the float precision version is
        defined it should be preferred.
        """
    )
