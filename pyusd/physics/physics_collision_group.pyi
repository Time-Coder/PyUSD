from ..typed import Typed
from ..dtypes import namespace, string
from .physics import Physics


class PhysicsCollisionGroup(Typed):
    """Defines a collision group for coarse filtering. When a collision 
    occurs between two objects that have a PhysicsCollisionGroup assigned,
    they will collide with each other unless this PhysicsCollisionGroup pair 
    is filtered. See filteredGroups attribute.
    
    A CollectionAPI:colliders maintains a list of PhysicsCollisionAPI rel-s that 
    defines the members of this Collisiongroup.
    
    """

    @property
    def physics(self) -> Physics: ...

