from ..typed import Typed
from ..gf import quatf
from ..dtypes import namespace
from .physics import Physics


class PhysicsJoint(Typed):
    """A joint constrains the movement of rigid bodies. Joint can be 
    created between two rigid bodies or between one rigid body and world.
    By default joint primitive defines a D6 joint where all degrees of 
    freedom are free. Three linear and three angular degrees of freedom.
    Note that default behavior is to disable collision between jointed bodies.
    
    """

    @property
    def physics(self) -> Physics: ...

