from .particle_field import ParticleField
from ..dtypes import token
from .radiance import Radiance


class ParticleField3DGaussianSplat(ParticleField):
    """This is a concrete ParticleField representing the original 3D
    Gaussian Splats technique (https://arxiv.org/abs/2308.04079).
    
    It inherits from the ParticleField base prim, and has a set of
    applied schema automatically applied to provide the required
    attributes to define the necessary data from the original 3DGS paper.
    
    It also contains some rendering hints that can optionally inform
    how the splats should be rendered. These hints typically
    corrolate with choices that were made when the data was trained.
    """


    class ProjectionModeHint(token):
        Perspective = "perspective"
        Tangential = "tangential"

    class SortingModeHint(token):
        ZDepth = "zDepth"
        CameraDistance = "cameraDistance"
        RayHitDistance = "rayHitDistance"

    @property
    def projectionModeHint(self)->Attribute[ProjectionModeHint]:
        """A hint for the renderer on how to project the gaussian to
                achieve a perspective correct view. Renderers are free to
                ignore this, but the hint is often valuable to tune the
                rendering of the scene. It often corresponds to a choice made
                when training the data.

               'Perspective' projection is similar to standard object rendering
               from a camera view. Gaussians are projected with scaling and
               distortion based on depth.

               'Tangential' projection treats the image plane as a tangent to
               the viewing sphere. Gaussians are projected orthogonally,
               preserving shape and scale better, which helps reduce distortion
               for certain rendering applications like novel view synthesis."""

    @projectionModeHint.setter
    def projectionModeHint(self, value:ProjectionModeHint)->None: ...

    @property
    def sortingModeHint(self)->Attribute[SortingModeHint]:
        """A hint for the renderer on how to sort the gaussians while
        drawing. Renderers are free to ignore this, but the hint is often
        valuable to tune the rendering of the scene. It often corresponds to a
        choice made when training the data.

        Rasterizers usually sort gaussians from back to front. This attribute
        is a hint for the metric used to sort the gaussians with respect to the
        camera.

        'zDepth': The particles are sorted based on the z component of the
        particle position when transformed in to the cameras local space.

        'cameraDistance': The particles are sorted based on the euclidian
        distance from the particle to the camera.

        'rayHitDistance': The particles are sorted based on the distance from
        the camera to where the ray hits the particle (used in ray tracing).
        Rasterizers that do not support ray tracing may treat this as
        'cameraDistance'."""

    @sortingModeHint.setter
    def sortingModeHint(self, value:SortingModeHint)->None: ...

