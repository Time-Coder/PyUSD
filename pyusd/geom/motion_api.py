from ..prim import Prim
from ..attribute import Attribute
from ..dtypes import namespace
from ..api_schema_base import APISchemaBase


class MotionAPI(APISchemaBase):
    """UsdGeomMotionAPI encodes data that can live on any prim that
    may affect computations involving:
    - computed motion for motion blur
    - sampling for motion blur
    
    The \\ref GetMotionBlurScaleAttr() "motion:blurScale" attribute allows
    artists to scale the __amount__ of motion blur to be rendered for parts
    of the scene without changing the recorded animation.  See
    \\ref UsdGeomMotionAPI_blurScale for use and implementation details.
    
    """
    
    @classmethod
    def apply(cls, prim:Prim)->Prim:
        prim.metadata.apiSchemas.append(cls.__name__)

        motion = prim.create_prop(Attribute(namespace, "motion", is_leaf=False))
        motion.create_prop(Attribute(float, "blurScale", value=1.0, metadata={
            "doc": """BlurScale is an __inherited__ float attribute that stipulates
        the rendered motion blur (as typically specified via UsdGeomCamera's
        _shutter:open_ and _shutter:close_ properties) should be scaled for
        __all objects__ at and beneath the prim in namespace on which the
        _motion:blurScale_ value is specified.
        
        Without changing any other data in the scene, _blurScale_ allows artists to
        "dial in" the amount of blur on a per-object basis.  A _blurScale_
        value of zero removes all blur, a value of 0.5 reduces blur by half, 
        and a value of 2.0 doubles the blur.  The legal range for _blurScale_
        is [0, inf), although very high values may result in extremely expensive
        renders, and may exceed the capabilities of some renderers.
        
        Although renderers are free to implement this feature however they see
        fit, see \\ref UsdGeomMotionAPI_blurScale for our guidance on implementing
        the feature universally and efficiently.
        
        \\sa ComputeMotionBlurScale()
        """
        }))
        motion.create_prop(Attribute(float, "velocityScale", value=1.0, metadata={
            "customData": {
                "apiName": "velocityScale"
            },
            "doc": """\\deprecated
        
        VelocityScale is an **inherited** float attribute that
        velocity-based schemas (e.g. PointBased, PointInstancer) can consume
        to compute interpolated positions and orientations by applying
        velocity and angularVelocity, which is required for interpolating 
        between samples when topology is varying over time.  Although these 
        quantities are generally physically computed by a simulator, sometimes 
        we require more or less motion-blur to achieve the desired look.  
        VelocityScale allows artists to dial-in, as a post-sim correction, 
        a scale factor to be applied to the velocity prior to computing 
        interpolated positions from it."""
        }))
        motion.create_prop(Attribute(int, "nonlinearSampleCount", value=3, metadata={
            "customData": {
                "apiName": "nonlinearSampleCount"
            },
            "doc": """Determines the number of position or transformation samples
        created when motion is described by attributes contributing non-linear
        terms.
        
        To give an example, imagine an application (such as a
        renderer) consuming 'points' and the USD document also
        contains 'accelerations' for the same prim. Unless the
        application can consume these 'accelerations' itself, an
        intermediate layer has to compute samples within the sampling
        interval for the point positions based on the value of
        'points', 'velocities' and 'accelerations'. The number of these
        samples is given by 'nonlinearSampleCount'. The samples are
        equally spaced within the sampling interval.

        Another example involves the PointInstancer where
        'nonlinearSampleCount' is relevant when 'angularVelocities'
        or 'accelerations' are authored.

        'nonlinearSampleCount' is an **inherited** attribute, also
        see ComputeNonlinearSampleCount()"""
        }))

        return prim
