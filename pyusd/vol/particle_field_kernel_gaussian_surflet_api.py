from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class ParticleFieldKernelGaussianSurfletAPI(APISchemaBase):
    """Defines the gaussian surflet kernel for a given ParticleField.

    An untransformed kernel (i.e. identity position, scale, rotation, opacity)
    will define opacity at point 'p' on the XY plane by
    g(u=0;o=1;x = p.length()), with opacity off the XY-plane defined as 0.
    Note that since the standard deviation is 1, the 3-sigma point is 3.0
    and 99.7% of the splat support is within a circular disk on the XY plane
    of radius 3.

    Per-splat opacity is multiplicative with the gaussian falloff; rotation
    and scale will transform the gaussian disk kernel into a planar ellipse,
    and position moves the per-splat peak falloff from the origin. 
    """
    schema_kind: SchemaKind = SchemaKind.SingleApplyAPI

    meta = {
        "customData": {
            "apiSchemaType": "singleApply",
            "apiSchemaCanOnlyApplyTo": """'''
                #include "pxr/usd/usdVol/particleFieldKernelBaseAPI.h"
                        '''""",
            "extraIncludes": """'''
                #include "pxr/usd/usdVol/particleFieldKernelBaseAPI.h"
                        '''""",
            "reflectedAPISchemas": "None"
        }
    }
