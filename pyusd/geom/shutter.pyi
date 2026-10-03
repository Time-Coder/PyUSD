from ..attribute_spec import AttributeSpec
from ..dtypes import double

class Shutter(AttributeSpec):

    @property
    def open(self)->AttributeSpec[double]:
        """Frame relative shutter open time in UsdTimeCode units (negative
                 value indicates that the shutter opens before the current
                 frame time). Used for motion blur."""

    @open.setter
    def open(self, value:double)->None: ...

    @property
    def close(self)->AttributeSpec[double]:
        """Frame relative shutter close time, analogous comments from
                 shutter:open apply. A value greater or equal to shutter:open
                 should be authored, otherwise there is no exposure and a
                 renderer should produce a black image. Used for motion blur."""

    @close.setter
    def close(self, value:double)->None: ...
