from typing import List

from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..gf import point3f, point3h


class ParticleFieldPositionAttributeAPI(APISchemaBase):
    """A ParticleField related applied schema that provides a position
    attribute to define the locations of the particles.

    Attributes are provided in both `float` and `half` types for some
    easy data footprint affordance, data consumers should prefer
    `float` version if available.

    The size of the positions attribute that is being used defines the
    number of particles in the field. If no positions attribute is
    provided then the ParticleField has no particles.
    """

    schema_kind: SchemaKind = SchemaKind.SingleApplyAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": ["ParticleField"],
            "extraIncludes": '''
                #include "pxr/usd/usdVol/particleFieldPositionBaseAPI.h"
            ''',
            "reflectedAPISchemas": ["ParticleFieldPositionBaseAPI"]
        },
        "prepend apiSchemas": ["ParticleFieldPositionBaseAPI"]
    }

    positions: AttributeSpec[List[point3f]] = AttributeSpec(List[point3f], value=[], doc="Defines the position for each particle in local space.")

    positionsh: AttributeSpec[List[point3h]] = AttributeSpec(List[point3h],
        value=[],
        doc="""Defines the position for each particle in local space. If the
        float precision attribute is defined it should be preferred.
        """
    )
