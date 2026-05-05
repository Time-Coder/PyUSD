from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class ParticleFieldKernelGaussianEllipsoidAPI(APISchemaBase):
    """Defines the gaussian ellipsoid kernel for a given ParticleField.
    
    An untransformed kernel (i.e. identity position, scale, rotation, opacity)
    will define opacity at point 'p' by g(u=0;o=1;x = p.length()).  Note that
    since the standard deviation is 1, the 3-sigma point is 3.0 and 99.7% of
    the splat support is within a spherical region of radius 3.
    
    Per-splat opacity is multiplicative with the gaussian falloff; rotation
    and scale will transform the gaussian sphere kernel into an ellipsoid;
    and position moves the per-splat peak falloff from the origin. 
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": """'''
    #include "pxr/usd/usdVol/particleFieldKernelBaseAPI.h"
            '''""",
            "extraIncludes": """'''
    #include "pxr/usd/usdVol/particleFieldKernelBaseAPI.h"
            '''""",
            "reflectedAPISchemas": None
        }
    }
