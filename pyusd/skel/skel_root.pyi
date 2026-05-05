from ..geom.boundable import Boundable
from .primvars import Primvars
from .skel import Skel


class SkelRoot(Boundable):
    """Boundable prim type used to identify a scope beneath which
    skeletally-posed primitives are defined.
    
    A SkelRoot must be defined at or above a skinned primitive for any skinning
    behaviors in UsdSkel.
    
    See the extended \\ref UsdSkel_SkelRoot "Skel Root Schema" documentation for
    more information.
    """

