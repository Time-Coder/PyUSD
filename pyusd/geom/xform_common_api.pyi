from ..api_schema_base import APISchemaBase
from .exposure import Exposure
from .model import Model
from .motion import Motion
from .primvars import Primvars
from .shutter import Shutter
from .trim_curve import TrimCurve


class XformCommonAPI(APISchemaBase):
    """This class provides API for authoring and retrieving a standard set
    of component transformations which include a scale, a rotation, a 
    scale-rotate pivot and a translation. The goal of the API is to enhance 
    component-wise interchange. It achieves this by limiting the set of allowed 
    basic ops and by specifying the order in which they are applied. In addition
    to the basic set of ops, the 'resetXformStack' bit can also be set to 
    indicate whether the underlying xformable resets the parent transformation 
    (i.e. does not inherit it's parent's transformation). 
    
    \\sa UsdGeomXformCommonAPI::GetResetXformStack()
    \\sa UsdGeomXformCommonAPI::SetResetXformStack()
    
    The operator-bool for the class will inform you whether an existing 
    xformable is compatible with this API.
    
    The scale-rotate pivot is represented by a pair of (translate, 
    inverse-translate) xformOps around the scale and rotate operations.
    The rotation operation can be any of the six allowed Euler angle sets.
    \\sa UsdGeomXformOp::Type. 
    
    The xformOpOrder of an xformable that has all of the supported basic ops 
    is as follows:
    ["xformOp:translate", "xformOp:translate:pivot", "xformOp:rotateXYZ",
    "xformOp:scale", "!invert!xformOp:translate:pivot"].
    
    It is worth noting that all of the ops are optional. For example, an 
    xformable may have only a translate or a rotate. It would still be 
    considered as compatible with this API. Individual SetTranslate(), 
    SetRotate(), SetScale() and SetPivot() methods are provided by this API 
    to allow such sparse authoring.
    """

