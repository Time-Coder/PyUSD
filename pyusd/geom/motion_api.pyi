from ..api_schema_base import APISchemaBase
from ..dtypes import namespace
from .exposure import Exposure
from .model import Model
from .motion import Motion
from .primvars import Primvars
from .shutter import Shutter
from .trim_curve import TrimCurve


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

