from ..geom.imageable import Imageable
from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import point3f, quatf
from .physics import Physics


class PhysicsJoint(Imageable):
    """A joint constrains the movement of rigid bodies. Joint can be 
    created between two rigid bodies or between one rigid body and world.
    By default joint primitive defines a D6 joint where all degrees of 
    freedom are free. Three linear and three angular degrees of freedom.
    Note that default behavior is to disable collision between jointed bodies.
    
    """

    @property
    def physics(self) -> Physics: ...

