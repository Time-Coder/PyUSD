from ..gprim import Gprim
from ..common import SchemaKind


class ParticleField(Gprim):
    """A ParticleField prim is used as a base to describe different types
            of concrete ParticleField implementations, such as, but not limited
            to, 3D Gaussian Splats.

            It is a concrete prim type that can have different
            ParticleField related applied schemas applied to it, to
            specialize its definition.

            The related ParticleField applied schemas represent the different
            features of a ParticleField, such as positions, orientations,
            scales, kernel (shape and fall-off) and radiance. Any of these
            applied schema that are required to define a valid ParticleField
            also have a base applied schema that they auto apply. This base
            applied schema allows for valiation rules to be written that
            ensure the necessary components are present.

            Without at least some of these applied schemas the ParticleField
            is just an empty abstract container, but adding different
            combinations of these applied schemas allows us to describe a
            varying family of types of ParticleFields."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped
