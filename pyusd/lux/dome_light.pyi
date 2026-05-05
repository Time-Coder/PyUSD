from .nonboundable_light_base import NonboundableLightBase
from ..dtypes import asset, namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
from .light_list import LightList


class DomeLight(NonboundableLightBase):
    """Light emitted inward from a distant external environment,
    such as a sky or IBL light probe.
    
    In this version of the dome light, the dome's default orientation is such
    that its top pole is aligned with the world's +Y axis. This adheres to the
    OpenEXR specification for latlong environment maps.  From the OpenEXR
    documentation:
    
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
    
    """


    class Format(token):
        Automatic = "automatic"
        Latlong = "latlong"
        MirroredBall = "mirroredBall"
        Angular = "angular"
        CubeMapVerticalCross = "cubeMapVerticalCross"

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
    def portals(self)->Relationship:
        """Optional portals to guide light sampling."""

    @portals.setter
    def portals(self, value:Relationship)->None: ...

