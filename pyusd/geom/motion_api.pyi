from ..api_schema_base import APISchemaBase
from .motion import Motion

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

    @property
    def motion(self) -> Motion: ...

