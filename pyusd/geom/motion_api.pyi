from ..prim import Prim
from ..api_schema_base import APISchemaBase


class MotionAPI(APISchemaBase):
    'UsdGeomMotionAPI encodes data that can live on any prim that\n    may affect computations involving:\n    - computed motion for motion blur\n    - sampling for motion blur\n    \n    The \\ref GetMotionBlurScaleAttr() "motion:blurScale" attribute allows\n    artists to scale the __amount__ of motion blur to be rendered for parts\n    of the scene without changing the recorded animation.  See\n    \\ref UsdGeomMotionAPI_blurScale for use and implementation details.\n    \n    '
    @classmethod
    def apply(cls, prim:Prim)->Prim: ...
