from ..typed import Typed
from .exposure import Exposure
from .model import Model
from .motion import Motion
from .primvars import Primvars
from .shutter import Shutter
from .trim_curve import TrimCurve


class Scope(Typed):
    """Scope is the simplest grouping primitive, and does not carry the
    baggage of transformability.  Note that transforms should inherit down
    through a Scope successfully - it is just a guaranteed no-op from a
    transformability perspective.
    """

