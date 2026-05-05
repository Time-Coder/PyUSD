from ..attribute import Attribute
from ..relationship import Relationship
from typing import List


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
