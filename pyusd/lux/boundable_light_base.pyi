from ..geom.boundable import Boundable

class BoundableLightBase(Boundable):
    """Base class for intrinsic lights that are boundable.

    The primary purpose of this class is to provide a direct API to the
    functions provided by LightAPI for concrete derived light types.

    """
