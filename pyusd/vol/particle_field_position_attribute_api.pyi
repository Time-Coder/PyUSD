from ..api_schema_base import APISchemaBase
from .radiance import Radiance


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

    @property
    def positions(self)->Attribute[List[point3f]]:
        """Defines the position for each particle in local space."""

    @positions.setter
    def positions(self, value:List[point3f])->None: ...

    @property
    def positionsh(self)->Attribute[List[point3h]]:
        """Defines the position for each particle in local space. If the
                float precision attribute is defined it should be preferred."""

    @positionsh.setter
    def positionsh(self, value:List[point3h])->None: ...

