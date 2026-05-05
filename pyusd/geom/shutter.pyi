from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import double
from typing import List


class Shutter(Attribute):

    @property
    def open(self)->Attribute[double]:
        """Frame relative shutter open time in UsdTimeCode units (negative
                 value indicates that the shutter opens before the current
                 frame time). Used for motion blur."""

    @open.setter
    def open(self, value:double)->None: ...

    @property
    def close(self)->Attribute[double]:
        """Frame relative shutter close time, analogous comments from
                 shutter:open apply. A value greater or equal to shutter:open
                 should be authored, otherwise there is no exposure and a
                 renderer should produce a black image. Used for motion blur."""

    @close.setter
    def close(self, value:double)->None: ...
