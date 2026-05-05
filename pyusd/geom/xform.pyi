from ..typed import Typed
from .exposure import Exposure
from .model import Model
from .motion import Motion
from .primvars import Primvars
from .shutter import Shutter
from .trim_curve import TrimCurve


class Xform(Typed):
    "Concrete prim schema for a transform, which implements Xformable "

