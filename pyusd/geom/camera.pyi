from .xformable import Xformable
from ..attribute import Attribute
from ..dtypes import token
from ..gf import float2, float4
from typing import List


class Shutter(Attribute):

    @property
    def open(self)->Attribute[float]:
        """Frame relative shutter open time in UsdTimeCode units (negative
        value indicates that the shutter opens before the current
        frame time). Used for motion blur."""

    @open.setter
    def open(self, value:float)->None: ...

    @property
    def close(self)->Attribute[float]:
        """Frame relative shutter close time, analogous comments from
        shutter:open apply. A value greater or equal to shutter:open
        should be authored, otherwise there is no exposure and a
        renderer should produce a black image. Used for motion blur."""

    @close.setter
    def close(self, value:float)->None: ...


class Exposure(Attribute):

    @property
    def iso(self)->Attribute[float]:
        """The speed rating of the sensor or film when calculating exposure.
        Higher numbers give a brighter image, lower numbers darker."""

    @iso.setter
    def iso(self, value:float)->None: ...

    @property
    def time(self)->Attribute[float]:
        """Time in seconds that the sensor is exposed to light when calculating exposure.
        Longer exposure times create a brighter image, shorter times darker.
        Note that shutter:open and shutter:close model essentially the 
        same property of a physical camera, but are for specifying the 
        size of the motion blur streak which is for practical purposes
        useful to keep separate."""

    @time.setter
    def time(self, value:float)->None: ...

    @property
    def fStop(self)->Attribute[float]:
        """f-stop of the aperture when calculating exposure. Smaller numbers
        create a brighter image, larger numbers darker.
        Note that the `fStop` attribute also models the diameter of the camera
        aperture, but for specifying depth of field.  For practical 
        purposes it is useful to keep the exposure and the depth of field
        controls separate.
        """

    @fStop.setter
    def fStop(self, value:float)->None: ...

    @property
    def responsivity(self)->Attribute[float]:
        """Scalar multiplier representing overall responsivity of the 
        sensor system to light when calculating exposure. Intended to be
        used as a per camera/lens system measured scaling value."""
        
    @responsivity.setter
    def responsivity(self, value:float)->None: ...


class Camera(Xformable):
    """Transformable camera.
    
    Describes optical properties of a camera via a common set of attributes
    that provide control over the camera's frustum as well as its depth of
    field. For stereo, the left and right camera are individual prims tagged
    through the \\ref UsdGeomCamera::GetStereoRoleAttr() "stereoRole attribute".
    
    There is a corresponding class GfCamera, which can hold the state of a
    camera (at a particular time). \\ref UsdGeomCamera::GetCamera() and
    \\ref UsdGeomCamera::SetFromCamera() convert between a USD camera prim and
    a GfCamera.

    To obtain the camera's location in world space, call the following on a
    UsdGeomCamera 'camera':
    \\code
    GfMatrix4d camXform = camera.ComputeLocalToWorldTransform(time);
    \\endcode
    \\note
    <b>Cameras in USD are always "Y up", regardless of the stage's orientation
    (i.e. UsdGeomGetStageUpAxis()).</b> 'camXform' positions the camera in the 
    world, and the inverse transforms the world such that the camera is at the 
    origin, looking down the -Z axis, with +Y as the up axis, and +X pointing to 
    the right. This describes a __right handed coordinate system__. 

    \\section UsdGeom_CameraUnits Units of Measure for Camera Properties

    Despite the familiarity of millimeters for specifying some physical
    camera properties, UsdGeomCamera opts for greater consistency with all
    other UsdGeom schemas, which measure geometric properties in scene units,
    as determined by UsdGeomGetStageMetersPerUnit().  We do make a
    concession, however, in that lens and filmback properties are measured in
    __tenths of a scene unit__ rather than "raw" scene units.  This means
    that with the fallback value of .01 for _metersPerUnit_ - i.e. scene unit
    of centimeters - then these "tenth of scene unit" properties are
    effectively millimeters.

    \\note If one adds a Camera prim to a UsdStage whose scene unit is not
    centimeters, the fallback values for filmback properties will be
    incorrect (or at the least, unexpected) in an absolute sense; however,
    proper imaging through a "default camera" with focusing disabled depends
    only on ratios of the other properties, so the camera is still usable.
    However, it follows that if even one property is authored in the correct
    scene units, then they all must be.

    \\section UsdGeom_CameraExposure Camera Exposure Model

    UsdGeomCamera models exposure by a camera in terms of exposure time, ISO,
    f-stop, and exposure compensation, mirroring the controls on a real camera.
    These parameters are provided by \\ref UsdGeomCamera::GetExposureTimeAttr(),
    \\ref UsdGeomCamera::GetExposureIsoAttr(),
    \\ref UsdGeomCamera::GetExposureFStopAttr(), 
    and \\ref UsdGeomCamera::GetExposureAttr(), respectively. 
    \\ref UsdGeomCamera::GetExposureResponsivityAttr() provides an additional
    scaling factor to model the overall responsivity of the system,
    including response of the sensor and loss by the lens.

    The calculated scaling factor can be obtained from 
    \\ref UsdGeomCamera::ComputeLinearExposureScale(). It is computed as:
    \\code
        linearExposureScale = exposureResponsivity * 
            (exposureTime * (exposureIso/100) * pow(2, exposure)) 
            / (exposureFStop * exposureFStop)
    \\endcode

    This scaling factor is combined from two parts: The first, known as the
    __imaging ratio__ (in _steradian-second_), converts from incident luminance
    at the front of the lens system, in _nit_ (_cd/m^2_), to photometric
    exposure at the sensor in _lux-second_. The second, `exposureResponsivity` 
    (in _inverse lux-second_), converts from photometric exposure at the sensor,
    in _lux-second_, to a unitless output signal.

    For a thorough treatment of this topic, see
    https://github.com/wetadigital/physlight/blob/main/docs/physLight-v1.3-1bdb6ec3-20230805.pdf,
    Section 2.2. Note that we are essentially implementing Equation 2.7, but are 
    choosing C such that it exactly cancels with the factor of pi in the
    numerator, replacing it with a responsivity factor that defaults to 1.

    Renderers should simply multiply the brightness of the image by the exposure 
    scale. The default values for the exposure-related attributes combine to
    give a scale of 1.0.
    
    \\sa \\ref UsdGeom_LinAlgBasics
     """
    
    def __init__(self, name:str="")->None: ...

    @property
    def projection(self)->Attribute[token]: ...

    @projection.setter
    def projection(self, value:token)->None: ...

    @property
    def horizontalAperture(self)->Attribute[float]:
        """Horizontal aperture in tenths of a scene unit; see 
        \\ref UsdGeom_CameraUnits . Default is the equivalent of 
        the standard 35mm spherical projector aperture."""

    @horizontalAperture.setter
    def horizontalAperture(self, value:float)->None: ...

    @property
    def verticalAperture(self)->Attribute[float]:
        """Vertical aperture in tenths of a scene unit; see 
        \\ref UsdGeom_CameraUnits . Default is the equivalent of 
        the standard 35mm spherical projector aperture."""

    @verticalAperture.setter
    def verticalAperture(self, value:float)->None: ...

    @property
    def horizontalApertureOffset(self)->Attribute[float]:
        """Horizontal aperture offset in the same units as
        horizontalAperture. Defaults to 0."""

    @horizontalApertureOffset.setter
    def horizontalApertureOffset(self, value:float)->None: ...

    @property
    def verticalApertureOffset(self)->Attribute[float]:
        """Vertical aperture offset in the same units as
        verticalAperture. Defaults to 0."""

    @verticalApertureOffset.setter
    def verticalApertureOffset(self, value:float)->None: ...

    @property
    def focalLength(self)->Attribute[float]:
        """Perspective focal length in tenths of a scene unit; see 
        \\ref UsdGeom_CameraUnits ."""

    @focalLength.setter
    def focalLength(self, value:float)->None: ...

    @property
    def clippingRange(self)->Attribute[float2]:
        """Near and far clipping distances in scene units; see 
        \\ref UsdGeom_CameraUnits ."""
        
    @clippingRange.setter
    def clippingRange(self, value:float2)->None: ...

    @property
    def clippingPlanes(self)->Attribute[List[float4]]:
        """Additional, arbitrarily oriented clipping planes.
        A vector (a,b,c,d) encodes a clipping plane that cuts off
        (x,y,z) with a * x + b * y + c * z + d * 1 < 0 where (x,y,z)
        are the coordinates in the camera's space."""

    @clippingPlanes.setter
    def clippingPlanes(self, value:List[float4])->None: ...

    @property
    def fStop(self)->Attribute[float]:
        """Lens aperture. Defaults to 0.0, which turns off depth of field effects."""

    @fStop.setter
    def fStop(self, value:float)->None: ...

    @property
    def focusDistance(self)->Attribute[float]:
        """Distance from the camera to the focus plane in scene units; see 
        \\ref UsdGeom_CameraUnits ."""

    @focusDistance.setter
    def focusDistance(self, value:float)->None: ...

    @property
    def stereoRole(self)->Attribute[token]:
        """If different from mono, the camera is intended to be the left
        or right camera of a stereo setup."""

    @stereoRole.setter
    def stereoRole(self, value:token)->None: ...

    @property
    def shutter(self)->Shutter: ...

    @property
    def exposure(self)->Exposure:
        """Exposure compensation, as a log base-2 value.  The default
        of 0.0 has no effect.  A value of 1.0 will double the
        image-plane intensities in a rendered image; a value of
        -1.0 will halve them."""
