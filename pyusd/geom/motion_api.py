from ..prim import Prim
from ..attribute import Attribute
from ..dtypes import namespace
from ..api_schema_base import APISchemaBase


class MotionAPI(APISchemaBase):
    'UsdGeomMotionAPI encodes data that can live on any prim that\n    may affect computations involving:\n    - computed motion for motion blur\n    - sampling for motion blur\n    \n    The \\ref GetMotionBlurScaleAttr() "motion:blurScale" attribute allows\n    artists to scale the __amount__ of motion blur to be rendered for parts\n    of the scene without changing the recorded animation.  See\n    \\ref UsdGeomMotionAPI_blurScale for use and implementation details.\n    \n    '
    @classmethod
    def apply(cls, prim:Prim)->Prim:
        prim.metadata.apiSchemas.append(cls.__name__)

        motion = Attribute(namespace, "motion", is_leaf=False)
        motion.create_prop(Attribute(float, "blurScale", value=1.0, metadata={
            "doc": """Scale factor applied to rendered motion blur for objects
        at and beneath this prim."""
        }))
        motion.create_prop(Attribute(float, "velocityScale", value=1.0, metadata={
            "customData": {
                "apiName": "velocityScale"
            },
            "doc": """Deprecated inherited scale factor applied to authored
        velocities before interpolation."""
        }))
        motion.create_prop(Attribute(int, "nonlinearSampleCount", value=3, metadata={
            "customData": {
                "apiName": "nonlinearSampleCount"
            },
            "doc": """Determines how many samples to create when motion contains
        nonlinear terms such as accelerations."""
        }))
        prim.create_prop(motion)

        # DOCSYNC-BEGIN MotionAPI
        prim.motion.blurScale.metadata.update({"doc": 'BlurScale is an __inherited__ float attribute that stipulates\n        the rendered motion blur (as typically specified via UsdGeomCamera\'s\n        _shutter:open_ and _shutter:close_ properties) should be scaled for\n        __all objects__ at and beneath the prim in namespace on which the\n        _motion:blurScale_ value is specified.\n        \n        Without changing any other data in the scene, _blurScale_ allows artists to\n        "dial in" the amount of blur on a per-object basis.  A _blurScale_\n        value of zero removes all blur, a value of 0.5 reduces blur by half, \n        and a value of 2.0 doubles the blur.  The legal range for _blurScale_\n        is [0, inf), although very high values may result in extremely expensive\n        renders, and may exceed the capabilities of some renderers.\n        \n        Although renderers are free to implement this feature however they see\n        fit, see \\ref UsdGeomMotionAPI_blurScale for our guidance on implementing\n        the feature universally and efficiently.\n        \n        \\sa ComputeMotionBlurScale()\n        '})
        prim.motion.velocityScale.metadata.update({"doc": '\\deprecated\n        \n        VelocityScale is an **inherited** float attribute that\n        velocity-based schemas (e.g. PointBased, PointInstancer) can consume\n        to compute interpolated positions and orientations by applying\n        velocity and angularVelocity, which is required for interpolating \n        between samples when topology is varying over time.  Although these \n        quantities are generally physically computed by a simulator, sometimes \n        we require more or less motion-blur to achieve the desired look.  \n        VelocityScale allows artists to dial-in, as a post-sim correction, \n        a scale factor to be applied to the velocity prior to computing \n        interpolated positions from it.'})
        prim.motion.nonlinearSampleCount.metadata.update({"doc": "Determines the number of position or transformation samples\n        created when motion is described by attributes contributing non-linear\n        terms.\n        \n        To give an example, imagine an application (such as a\n        renderer) consuming 'points' and the USD document also\n        contains 'accelerations' for the same prim. Unless the\n        application can consume these 'accelerations' itself, an\n        intermediate layer has to compute samples within the sampling\n        interval for the point positions based on the value of\n        'points', 'velocities' and 'accelerations'. The number of these\n        samples is given by 'nonlinearSampleCount'. The samples are\n        equally spaced within the sampling interval.\n\n        Another example involves the PointInstancer where\n        'nonlinearSampleCount' is relevant when 'angularVelocities'\n        or 'accelerations' are authored.\n\n        'nonlinearSampleCount' is an **inherited** attribute, also\n        see ComputeNonlinearSampleCount()"})
        # DOCSYNC-END MotionAPI
        return prim
