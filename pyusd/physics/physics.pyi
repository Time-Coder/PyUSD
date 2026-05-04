from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import float3, point3f, quatf, vector3f
from ..dtypes import string, token
from typing import List


class Physics(Attribute):

    class Approximation(token):
        None_ = "none"
        ConvexDecomposition = "convexDecomposition"
        ConvexHull = "convexHull"
        BoundingSphere = "boundingSphere"
        BoundingCube = "boundingCube"
        MeshSimplification = "meshSimplification"

    class Type(token):
        Force = "force"
        Acceleration = "acceleration"


    @property
    def gravityDirection(self)->Attribute[vector3f]:
        """Gravity direction vector in simulation world space. Will be
        normalized before use. A zero vector is a request to use the negative 
        upAxis. Unitless."""

    @gravityDirection.setter
    def gravityDirection(self, value:vector3f)->None: ...

    @property
    def gravityMagnitude(self)->Attribute[float]:
        """Gravity acceleration magnitude in simulation world space. 
        A negative value is a request to use a value equivalent to earth 
        gravity regardless of the metersPerUnit scaling used by this scene. 
        Units: distance/second/second."""

    @gravityMagnitude.setter
    def gravityMagnitude(self, value:float)->None: ...

    @property
    def rigidBodyEnabled(self)->Attribute[bool]:
        """Determines if this PhysicsRigidBodyAPI is enabled."""

    @rigidBodyEnabled.setter
    def rigidBodyEnabled(self, value:bool)->None: ...

    @property
    def kinematicEnabled(self)->Attribute[bool]:
        """Determines whether the body is kinematic or not. A kinematic 
        body is a body that is moved through animated poses or through 
        user defined poses. The simulation derives velocities for the
        kinematic body based on the external motion. When a continuous motion
        is not desired, this kinematic flag should be set to false."""

    @kinematicEnabled.setter
    def kinematicEnabled(self, value:bool)->None: ...

    @property
    def startsAsleep(self)->Attribute[bool]:
        """Determines if the body is asleep when the simulation starts."""

    @startsAsleep.setter
    def startsAsleep(self, value:bool)->None: ...

    @property
    def velocity(self)->Attribute[vector3f]:
        """Linear velocity in the same space as the node's xform. 
        Units: distance/second."""

    @velocity.setter
    def velocity(self, value:vector3f)->None: ...

    @property
    def angularVelocity(self)->Attribute[vector3f]:
        """Angular velocity in the same space as the node's xform. 
        Units: degrees/second."""

    @angularVelocity.setter
    def angularVelocity(self, value:vector3f)->None: ...

    @property
    def simulationOwner(self)->Relationship:
        """Single PhysicsScene that will simulate this body. By 
        default this is the first PhysicsScene found in the stage using 
        UsdStage::Traverse()."""

    @simulationOwner.setter
    def simulationOwner(self, value:Relationship)->None: ...

    @property
    def mass(self)->Attribute[float]:
        """If non-zero, directly specifies the mass of the object.
        Note that any child prim can also have a mass when they apply massAPI.
        In this case, the precedence rule is 'parent mass overrides the
        child's'. This may come as counter-intuitive, but mass is a computed 
        quantity and in general not accumulative. For example, if a parent 
        has mass of 10, and one of two children has mass of 20, allowing 
        child's mass to override its parent results in a mass of -10 for the 
        other child. Note if mass is 0.0 it is ignored. Units: mass.
        """

    @mass.setter
    def mass(self, value:float)->None: ...

    @property
    def density(self)->Attribute[float]:
        """If non-zero, specifies the density of the object.
        In the context of rigid body physics, density indirectly results in 
        setting mass via (mass = density x volume of the object). How the 
        volume is computed is up to implementation of the physics system.
        It is generally computed from the collision approximation rather than
        the graphical mesh. In the case where both density and mass are 
        specified for the same object, mass has precedence over density. 
        Unlike mass, child's prim's density overrides parent prim's density 
        as it is accumulative. Note that density of a collisionAPI can be also
        alternatively set through a PhysicsMaterialAPI. The material density
        has the weakest precedence in density definition. Note if density is
        0.0 it is ignored. Units: mass/distance/distance/distance."""

    @density.setter
    def density(self, value:float)->None: ...

    @property
    def centerOfMass(self)->Attribute[point3f]:
        """Center of mass in the prim's local space. Units: distance."""

    @centerOfMass.setter
    def centerOfMass(self, value:point3f)->None: ...

    @property
    def diagonalInertia(self)->Attribute[float3]:
        """If non-zero, specifies diagonalized inertia tensor along the 
        principal axes. Note if diagonalInertial is (0.0, 0.0, 0.0) it is 
        ignored. Units: mass*distance*distance."""

    @diagonalInertia.setter
    def diagonalInertia(self, value:float3)->None: ...

    @property
    def principalAxes(self)->Attribute[quatf]:
        """Orientation of the inertia tensor's principal axes in the 
        prim's local space."""

    @principalAxes.setter
    def principalAxes(self, value:quatf)->None: ...

    @property
    def collisionEnabled(self)->Attribute[bool]:
        """Determines if the PhysicsCollisionAPI is enabled."""

    @collisionEnabled.setter
    def collisionEnabled(self, value:bool)->None: ...

    @property
    def approximation(self)->Attribute[Approximation]:
        """Determines the mesh's collision approximation:
	"none" - The mesh geometry is used directly as a collider without any 
    approximation.
	"convexDecomposition" - A convex mesh decomposition is performed. This 
    results in a set of convex mesh colliders.
	"convexHull" - A convex hull of the mesh is generated and used as the 
    collider.
	"boundingSphere" - A bounding sphere is computed around the mesh and used 
    as a collider.
	"boundingCube" - An optimally fitting box collider is computed around the 
    mesh.
	"meshSimplification" - A mesh simplification step is performed, resulting 
    in a simplified triangle mesh collider."""

    @approximation.setter
    def approximation(self, value:Approximation)->None: ...

    @property
    def dynamicFriction(self)->Attribute[float]:
        """Dynamic friction coefficient. Unitless."""

    @dynamicFriction.setter
    def dynamicFriction(self, value:float)->None: ...

    @property
    def staticFriction(self)->Attribute[float]:
        """Static friction coefficient. Unitless."""

    @staticFriction.setter
    def staticFriction(self, value:float)->None: ...

    @property
    def restitution(self)->Attribute[float]:
        """Restitution coefficient. Unitless."""

    @restitution.setter
    def restitution(self, value:float)->None: ...

    @property
    def mergeGroup(self)->Attribute[string]:
        """If non-empty, any collision groups in a stage with a matching
        mergeGroup should be considered to refer to the same collection. Matching
        collision groups should behave as if there were a single group containing
        referenced colliders and filter groups from both collections."""

    @mergeGroup.setter
    def mergeGroup(self, value:string)->None: ...

    @property
    def invertFilteredGroups(self)->Attribute[bool]:
        """Normally, the filter will disable collisions against the selected
        filter groups. However, if this option is set, the filter will disable
        collisions against all colliders except for those in the selected filter
        groups."""

    @invertFilteredGroups.setter
    def invertFilteredGroups(self, value:bool)->None: ...

    @property
    def filteredGroups(self)->Relationship:
        """References a list of PhysicsCollisionGroups with which 
        collisions should be ignored."""

    @filteredGroups.setter
    def filteredGroups(self, value:Relationship)->None: ...

    @property
    def filteredPairs(self)->Relationship:
        """Relationship to objects that should be filtered."""

    @filteredPairs.setter
    def filteredPairs(self, value:Relationship)->None: ...

    @property
    def localPos0(self)->Attribute[point3f]:
        """Relative position of the joint frame to body0's frame."""

    @localPos0.setter
    def localPos0(self, value:point3f)->None: ...

    @property
    def localRot0(self)->Attribute[quatf]:
        """Relative orientation of the joint frame to body0's frame."""

    @localRot0.setter
    def localRot0(self, value:quatf)->None: ...

    @property
    def localPos1(self)->Attribute[point3f]:
        """Relative position of the joint frame to body1's frame."""

    @localPos1.setter
    def localPos1(self, value:point3f)->None: ...

    @property
    def localRot1(self)->Attribute[quatf]:
        """Relative orientation of the joint frame to body1's frame."""

    @localRot1.setter
    def localRot1(self, value:quatf)->None: ...

    @property
    def jointEnabled(self)->Attribute[bool]:
        """Determines if the joint is enabled."""

    @jointEnabled.setter
    def jointEnabled(self, value:bool)->None: ...

    @property
    def excludeFromArticulation(self)->Attribute[bool]:
        """Determines if the joint can be included in an Articulation."""

    @excludeFromArticulation.setter
    def excludeFromArticulation(self, value:bool)->None: ...

    @property
    def breakForce(self)->Attribute[float]:
        """Joint break force. If set, joint is to break when this force
        limit is reached. (Used for linear DOFs.) 
        Units: mass * distance / second / second"""

    @breakForce.setter
    def breakForce(self, value:float)->None: ...

    @property
    def breakTorque(self)->Attribute[float]:
        """Joint break torque. If set, joint is to break when this torque
        limit is reached. (Used for angular DOFs.) 
        Units: mass * distance * distance / second / second"""

    @breakTorque.setter
    def breakTorque(self, value:float)->None: ...

    @property
    def body0(self)->Relationship:
        """Relationship to any UsdGeomXformable."""

    @body0.setter
    def body0(self, value:Relationship)->None: ...

    @property
    def body1(self)->Relationship:
        """Relationship to any UsdGeomXformable."""

    @body1.setter
    def body1(self, value:Relationship)->None: ...

    @property
    def axis(self)->Attribute[Axis]:
        """Joint axis."""

    @axis.setter
    def axis(self, value:Axis)->None: ...

    @property
    def lowerLimit(self)->Attribute[float]:
        """Lower limit. Units: degrees. -inf means not limited in 
        negative direction."""

    @lowerLimit.setter
    def lowerLimit(self, value:float)->None: ...

    @property
    def upperLimit(self)->Attribute[float]:
        """Upper limit. Units: degrees. inf means not limited in 
        positive direction."""

    @upperLimit.setter
    def upperLimit(self, value:float)->None: ...

    @property
    def coneAngle0Limit(self)->Attribute[float]:
        """Cone limit from the primary joint axis in the local0 frame 
        toward the next axis. (Next axis of X is Y, and of Z is X.) A 
        negative value means not limited. Units: degrees."""

    @coneAngle0Limit.setter
    def coneAngle0Limit(self, value:float)->None: ...

    @property
    def coneAngle1Limit(self)->Attribute[float]:
        """Cone limit from the primary joint axis in the local0 frame 
        toward the second to next axis. A negative value means not limited. 
        Units: degrees."""

    @coneAngle1Limit.setter
    def coneAngle1Limit(self, value:float)->None: ...

    @property
    def minDistance(self)->Attribute[float]:
        """Minimum distance. If attribute is negative, the joint is not 
        limited. Units: distance."""

    @minDistance.setter
    def minDistance(self, value:float)->None: ...

    @property
    def maxDistance(self)->Attribute[float]:
        """Maximum distance. If attribute is negative, the joint is not 
        limited. Units: distance."""

    @maxDistance.setter
    def maxDistance(self, value:float)->None: ...

    @property
    def low(self)->Attribute[float]:
        """Lower limit. Units: degrees or distance depending on trans or
        rot axis applied to. -inf means not limited in negative direction."""

    @low.setter
    def low(self, value:float)->None: ...

    @property
    def high(self)->Attribute[float]:
        """Upper limit. Units: degrees or distance depending on trans or 
        rot axis applied to. inf means not limited in positive direction."""

    @high.setter
    def high(self, value:float)->None: ...

    @property
    def maxForce(self)->Attribute[float]:
        """Maximum force that can be applied to drive. Units: 
                if linear drive: mass*DIST_UNITS/second/second
                if angular drive: mass*DIST_UNITS*DIST_UNITS/second/second
                inf means not limited. Must be non-negative.
        """

    @maxForce.setter
    def maxForce(self, value:float)->None: ...

    @property
    def targetPosition(self)->Attribute[float]:
        """Target value for position. Units: 
        if linear drive: distance
        if angular drive: degrees."""

    @targetPosition.setter
    def targetPosition(self, value:float)->None: ...

    @property
    def targetVelocity(self)->Attribute[float]:
        """Target value for velocity. Units: 
        if linear drive: distance/second
        if angular drive: degrees/second."""

    @targetVelocity.setter
    def targetVelocity(self, value:float)->None: ...

    @property
    def damping(self)->Attribute[float]:
        """Damping of the drive. Units: 
		if linear drive: mass/second
		If angular drive: mass*DIST_UNITS*DIST_UNITS/second/degrees."""

    @damping.setter
    def damping(self, value:float)->None: ...

    @property
    def stiffness(self)->Attribute[float]:
        """Stiffness of the drive. Units:
		if linear drive: mass/second/second
		if angular drive: mass*DIST_UNITS*DIST_UNITS/degrees/second/second."""

    @stiffness.setter
    def stiffness(self, value:float)->None: ...
