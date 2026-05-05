from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..gf import point3f
from ..common import SchemaKind


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

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": """
                #include "pxr/usd/usdVol/particleFieldPositionBaseAPI.h"
            """,
            "extraIncludes": """
                #include "pxr/usd/usdVol/particleFieldPositionBaseAPI.h"
            """,
            "reflectedAPISchemas": None
        }
    }

    positions = Attribute(List[point3f], doc="Defines the position for each particle in local space.")

    positionsh = Attribute(List[point3h],
        doc="""Defines the position for each particle in local space. If the
        float precision attribute is defined it should be preferred.
        """
    )
