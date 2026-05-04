from ..typed import Typed
from ..dtypes import namespace, token
from ..common import Axis
from .physics import Physics


class PhysicsSphericalJoint(Typed):
    """Predefined spherical joint type (Removes linear degrees of 
    freedom, cone limit may restrict the motion in a given range.) It allows
    two limit values, which when equal create a circular, else an elliptic 
    cone limit around the limit axis.
    """

    @property
    def physics(self) -> Physics: ...

