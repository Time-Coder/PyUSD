from .nonboundable_light_base import NonboundableLightBase
from ..dtypes import asset, namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class DomeLight_1(NonboundableLightBase):
    """Light emitted inward from a distant external environment,
    such as a sky or IBL light probe.
    
    In this version of the dome light, the dome's default orientation is
    determined by its *poleAxis* property. The fallback value, "scene", means
    that the dome starts with its top pole aligned with the stage's up axis.
    
    Note that the rotation necessary to align the dome light with its *poleAxis*
    is intended to be applied by a renderer to only the dome itself, and *not*
    to inherit down to any USD namespace children of the dome light prim.
    
    If *poleAxis* is set to "Y" or "scene" and the stage's up axis is "Y", the
    dome's default orientation will adhere to the OpenEXR specification for
    latlong environment maps.  From the OpenEXR documentation:
    
    -------------------------------------------------------------------------
    Latitude-Longitude Map:
    
    The environment is projected onto the image using polar coordinates
    (latitude and longitude).  A pixel's x coordinate corresponds to
    its longitude, and the y coordinate corresponds to its latitude.
    Pixel (dataWindow.min.x, dataWindow.min.y) has latitude +pi/2 and
    longitude +pi; pixel (dataWindow.max.x, dataWindow.max.y) has
    latitude -pi/2 and longitude -pi.
    
    In 3D space, latitudes -pi/2 and +pi/2 correspond to the negative and
    positive y direction.  Latitude 0, longitude 0 points into positive
    z direction; and latitude 0, longitude pi/2 points into positive x
    direction.
    
    The size of the data window should be 2*N by N pixels (width by height),
    where N can be any integer greater than 0.
    -------------------------------------------------------------------------
    
    If *poleAxis* is set to "Z" or "scene" and the stage's up axis is "Z",
    latitudes -pi/2 and +pi/2 will instead correspond to the negative and
    positive Z direction, and latitude 0, longitude 0 will instead point into
    the negative Y direction in 3D space.
    
    """


    class Format(token):
        Automatic = "automatic"
        Latlong = "latlong"
        MirroredBall = "mirroredBall"
        Angular = "angular"
        CubeMapVerticalCross = "cubeMapVerticalCross"

    class PoleAxis(token):
        Scene = "scene"
        Y = "Y"
        Z = "Z"

    @property
    def inputs(self) -> Inputs: ...

    @property
    def light(self) -> Light: ...

    @property
    def guideRadius(self)->Attribute[float]:
        """The radius of guide geometry to use to visualize the dome light.  The default is 1 km for scenes whose metersPerUnit is the USD default of 0.01 (i.e., 1 world unit is 1 cm)."""

    @guideRadius.setter
    def guideRadius(self, value:float)->None: ...

    @property
    def poleAxis(self)->Attribute[PoleAxis]:
        """
        A token which indicates the starting alignment of the dome
        light's top pole. This alignment is for the dome itself and is *not*
        inherited by the namespace children of the dome.
        Valid values are:
        - scene: The dome light's top pole is aligned with the stage's up axis.
        - Y: The dome light's top pole is aligned with the +Y axis.
        - Z: The dome light's top pole is aligned with the +Z axis.
        """

    @poleAxis.setter
    def poleAxis(self, value:PoleAxis)->None: ...

    @property
    def portals(self)->Relationship:
        """Optional portals to guide light sampling."""

    @portals.setter
    def portals(self, value:Relationship)->None: ...

