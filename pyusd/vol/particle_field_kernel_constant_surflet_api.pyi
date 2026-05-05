from ..api_schema_base import APISchemaBase
from .radiance import Radiance


class ParticleFieldKernelConstantSurfletAPI(APISchemaBase):
    """Defines the constant surflet kernel for a given ParticleField.
    
    An untransformed kernel (i.e. identity position, scale, rotation, opacity)
    will define opacity at point 'p' on the XY plane as 1.0 if p.length <= 1,
    and 0.0 otherwise. The splat support for this kernel is a bounded circular
    disk on the XY plane of radius 1.
    
    Per-splat opacity is multiplicative with the step-function falloff; rotation
    and scale will transform the disk kernel into a planar ellipse,
    and position moves the splat center the origin. 
    
    """

