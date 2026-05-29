from ..geom.gprim import Gprim
from .particle_field_kernel_constant_surflet_api import (
    ParticleFieldKernelConstantSurfletAPI,
)
from .particle_field_kernel_gaussian_ellipsoid_api import (
    ParticleFieldKernelGaussianEllipsoidAPI,
)
from .particle_field_kernel_gaussian_surflet_api import (
    ParticleFieldKernelGaussianSurfletAPI,
)
from .particle_field_opacity_attribute_api import ParticleFieldOpacityAttributeAPI
from .particle_field_orientation_attribute_api import (
    ParticleFieldOrientationAttributeAPI,
)
from .particle_field_position_attribute_api import ParticleFieldPositionAttributeAPI
from .particle_field_scale_attribute_api import ParticleFieldScaleAttributeAPI
from .particle_field_spherical_harmonics_attribute_api import (
    ParticleFieldSphericalHarmonicsAttributeAPI,
)

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
    varying family of types of ParticleFields.
    """

    @property
    def particle_field_position_attribute_api(self)->ParticleFieldPositionAttributeAPI: ...

    @property
    def particle_field_orientation_attribute_api(self)->ParticleFieldOrientationAttributeAPI: ...

    @property
    def particle_field_scale_attribute_api(self)->ParticleFieldScaleAttributeAPI: ...

    @property
    def particle_field_opacity_attribute_api(self)->ParticleFieldOpacityAttributeAPI: ...

    @property
    def particle_field_kernel_gaussian_ellipsoid_api(self)->ParticleFieldKernelGaussianEllipsoidAPI: ...

    @property
    def particle_field_kernel_gaussian_surflet_api(self)->ParticleFieldKernelGaussianSurfletAPI: ...

    @property
    def particle_field_kernel_constant_surflet_api(self)->ParticleFieldKernelConstantSurfletAPI: ...

    @property
    def particle_field_spherical_harmonics_attribute_api(self)->ParticleFieldSphericalHarmonicsAttributeAPI: ...
