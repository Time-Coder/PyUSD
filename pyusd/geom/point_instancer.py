from .boundable import Boundable
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import int64
from ..gf import float3, point3f, quath, quatf, vector3f
from typing import List


class PointInstancer(Boundable):
    """Encodes vectorized instancing of multiple, potentially
    animated, prototypes (object/instance masters), which can be arbitrary
    prims/subtrees on a UsdStage.
    
    PointInstancer is a "multi instancer", as it allows multiple prototypes
    to be scattered among its "points".  We use a UsdRelationship
    \\em prototypes to identify and order all of the possible prototypes, by
    targeting the root prim of each prototype.  The ordering imparted by
    relationships associates a zero-based integer with each prototype, and
    it is these integers we use to identify the prototype of each instance,
    compactly, and allowing prototypes to be swapped out without needing to
    reauthor all of the per-instance data.
    
    The PointInstancer schema is designed to scale to billions of instances,
    which motivates the choice to split the per-instance transformation into
    position, (quaternion) orientation, and scales, rather than a
    4x4 matrix per-instance.  In addition to requiring fewer bytes even if
    all elements are authored (32 bytes vs 64 for a single-precision 4x4
    matrix), we can also be selective about which attributes need to animate
    over time, for substantial data reduction in many cases.
    
    Note that PointInstancer is \\em not a Gprim, since it is not a graphical
    primitive by any stretch of the imagination. It \\em is, however,
    Boundable, since we will sometimes want to treat the entire PointInstancer
    similarly to a procedural, from the perspective of inclusion or framing.

    \\section UsdGeomPointInstancer_varyingTopo Varying Instance Identity over Time
    
    PointInstancers originating from simulations often have the characteristic
    that points/instances are "born", move around for some time period, and then
    die (or leave the area of interest). In such cases, billions of instances
    may be birthed over time, while at any \\em specific time, only a much
    smaller number are actually alive.  To encode this situation efficiently,
    the simulator may re-use indices in the instance arrays, when a particle
    dies, its index will be taken over by a new particle that may be birthed in
    a much different location.  This presents challenges both for 
    identity-tracking, and for motion-blur.
    
    We facilitate identity tracking by providing an optional, animatable
    \\em ids attribute, that specifies the 64 bit integer ID of the particle
    at each index, at each point in time.  If the simulator keeps monotonically
    increasing a particle-count each time a new particle is birthed, it will
    serve perfectly as particle \\em ids.
    
    We facilitate motion blur for varying-topology particle streams by
    optionally allowing per-instance \\em velocities and \\em angularVelocities
    to be authored.  If instance transforms are requested at a time between
    samples and either of the velocity attributes is authored, then we will
    not attempt to interpolate samples of \\em positions or \\em orientations.
    If not authored, and the bracketing samples have the same length, then we
    will interpolate.

    \\section UsdGeomPointInstancer_transform Computing an Instance Transform
    
    Each instance's transformation is a combination of the SRT affine transform
    described by its scale, orientation, and position, applied \\em after
    (i.e. less locally than) the local to parent transformation computed at 
    the root of the prototype it is instancing. 

    If your processing of prototype geometry naturally takes into account the 
    transform of the prototype root, then this term can be omitted from the 
    computation of each instance transform, and this can be controlled when 
    computing instance transformation matrices using the 
    UsdGeomPointInstancer::PrototypeXformInclusion enumeration.

    To understand the computation of the instance transform, in order to put
    an instance of a PointInstancer into the space of the PointInstancer's 
    parent prim we do the following:
    
    1. Apply (most locally) the authored local to parent transformation for 
    <em>prototypes[protoIndices[i]]</em>
    2. If *scales* is authored, next apply the scaling matrix from *scales[i]*
    3. If *orientations* is authored: **if *angularVelocities* is authored**, 
    first multiply *orientations[i]* by the unit quaternion derived by scaling 
    *angularVelocities[i]* by the \\ref UsdGeom_PITimeScaling "time differential" 
    from the left-bracketing timeSample for *orientation* to the requested 
    evaluation time *t*, storing the result in *R*, **else** assign *R* 
    directly from *orientations[i]*.  Apply the rotation matrix derived 
    from *R*.
    4. Apply the translation derived from *positions[i]*. If *velocities* is 
    authored, apply the translation deriving from *velocities[i]* scaled by 
    the time differential from the left-bracketing timeSample for *positions* 
    to the requested evaluation time *t*.
    5. Least locally, apply the transformation authored on the PointInstancer 
    prim itself (or the UsdGeomImageable::ComputeLocalToWorldTransform() of the 
    PointInstancer to put the instance directly into world space)

    If neither *velocities* nor *angularVelocities* are authored, we fallback to
    standard position and orientation computation logic (using linear
    interpolation between timeSamples) as described by
    \\ref UsdGeom_VelocityInterpolation .

    \\anchor UsdGeom_PITimeScaling
    <b>Scaling Velocities for Interpolation</b>
    
    When computing time-differentials by which to apply velocity or
    angularVelocity to positions or orientations, we must scale by
    ( 1.0 / UsdStage::GetTimeCodesPerSecond() ), because velocities are recorded
    in units/second, while we are interpolating in UsdTimeCode ordinates.
    
    We provide both high and low-level API's for dealing with the
    transformation as a matrix, both will compute the instance matrices using
    multiple threads; the low-level API allows the client to cache unvarying
    inputs so that they need not be read duplicately when computing over
    time.

    See also \\ref UsdGeom_VelocityInterpolation .
    
    \\section UsdGeomPointInstancer_primvars Primvars on PointInstancer
    
    \\ref UsdGeomPrimvar "Primvars" authored on a PointInstancer prim should
    always be applied to each instance with \\em constant interpolation at
    the root of the instance.  When you are authoring primvars on a 
    PointInstancer, think about it as if you were authoring them on a 
    point-cloud (e.g. a UsdGeomPoints gprim).  The same 
    <A HREF="https://renderman.pixar.com/resources/RenderMan_20/appnote.22.html#classSpecifiers">interpolation rules for points</A> apply here, substituting
    "instance" for "point".
    
    In other words, the (constant) value extracted for each instance
    from the authored primvar value depends on the authored \\em interpolation
    and \\em elementSize of the primvar, as follows:
    \\li <b>constant</b> or <b>uniform</b> : the entire authored value of the
    primvar should be applied exactly to each instance.
    \\li <b>varying</b>, <b>vertex</b>, or <b>faceVarying</b>: the first
    \\em elementSize elements of the authored primvar array should be assigned to
    instance zero, the second \\em elementSize elements should be assigned to
    instance one, and so forth.

    
    \\section UsdGeomPointInstancer_masking Masking Instances: "Deactivating" and Invising

    Often a PointInstancer is created "upstream" in a graphics pipeline, and
    the needs of "downstream" clients necessitate eliminating some of the 
    instances from further consideration.  Accomplishing this pruning by 
    re-authoring all of the per-instance attributes is not very attractive,
    since it may mean destructively editing a large quantity of data.  We
    therefore provide means of "masking" instances by ID, such that the 
    instance data is unmolested, but per-instance transform and primvar data
    can be retrieved with the no-longer-desired instances eliminated from the
    (smaller) arrays.  PointInstancer allows two independent means of masking
    instances by ID, each with different features that meet the needs of
    various clients in a pipeline.  Both pruning features' lists of ID's are
    combined to produce the mask returned by ComputeMaskAtTime().
    
    \\note If a PointInstancer has no authored \\em ids attribute, the masking
    features will still be available, with the integers specifying element
    position in the \\em protoIndices array rather than ID.

    \\subsection UsdGeomPointInstancer_inactiveIds InactiveIds: List-edited, Unvarying Masking

    The first masking feature encodes a list of IDs in a list-editable metadatum
    called \\em inactiveIds, which, although it does not have any similar 
    impact to stage population as \\ref UsdPrim::SetActive() "prim activation",
    it shares with that feature that its application is uniform over all time.
    Because it is list-editable, we can \\em sparsely add and remove instances
    from it in many layers.
    
    This sparse application pattern makes \\em inactiveIds a good choice when
    further downstream clients may need to reverse masking decisions made
    upstream, in a manner that is robust to many kinds of future changes to
    the upstream data.
    
    See ActivateId(), ActivateIds(), DeactivateId(), DeactivateIds(), 
    ActivateAllIds()

    \\subsection UsdGeomPointInstancer_invisibleIds invisibleIds: Animatable Masking

    The second masking feature encodes a list of IDs in a time-varying
    Int64Array-valued UsdAttribute called \\em invisibleIds , since it shares
    with \\ref UsdGeomImageable::GetVisibilityAttr() "Imageable visibility"
    the ability to animate object visibility.
    
    Unlike \\em inactiveIds, overriding a set of opinions for \\em invisibleIds
    is not at all straightforward, because one will, in general need to
    reauthor (in the overriding layer) **all** timeSamples for the attribute
    just to change one Id's visibility state, so it cannot be authored
    sparsely.  But it can be a very useful tool for situations like encoding
    pre-computed camera-frustum culling of geometry when either or both of
    the instances or the camera is animated.
    
    See VisId(), VisIds(), InvisId(), InvisIds(), VisAllIds()
     
    \\section UsdGeomPointInstancer_protoProcessing Processing and Not Processing Prototypes
    
    Any prim in the scenegraph can be targeted as a prototype by the
    \\em prototypes relationship.  We do not, however, provide a specific
    mechanism for identifying prototypes as geometry that should not be drawn
    (or processed) in their own, local spaces in the scenegraph.  We
    encourage organizing all prototypes as children of the PointInstancer
    prim that consumes them, and pruning "raw" processing and drawing
    traversals when they encounter a PointInstancer prim; this is what the
    UsdGeomBBoxCache and UsdImaging engines do.
    
    There \\em is a pattern one can deploy for organizing the prototypes such
    that they will automatically be skipped by basic UsdPrim::GetChildren() or
    UsdPrimRange traversals.  Usd prims each have a \\ref Usd_PrimSpecifiers
    "specifier" of "def", "over", or "class".  The default traversals skip over
    prims that are "pure overs" or classes.  So to protect prototypes from all
    generic traversals and processing, place them under a prim that is a "class"
    or "over". "class" is recommended , while "over" should be used when
    backwards compatibility with older versions of USD is needed. For example,
    \\code
    01 def PointInstancer "Crowd_Mid"
    02 {
    03     rel prototypes = [ </Crowd_Mid/Prototypes/MaleThin_Business>, </Crowd_Mid/OtherPrototypes/MaleThin_Casual> ]
    04     
    05     over "Prototypes" 
    06     {
    07          def "MaleThin_Business" (
    08              references = [@MaleGroupA/usd/MaleGroupA.usd@</MaleGroupA>]
    09              variants = {
    10                  string modelingVariant = "Thin"
    11                  string costumeVariant = "BusinessAttire"
    12              }
    13          )
    14          { ... }
    15     }
    16
    17     class "OtherPrototypes"
    18     {
    19          def "MaleThin_Casual"
    20          ...
    21     }
    22 }
    \\endcode
    """
    
    abstract: bool = False

    def __init__(self, name:str="")->None:
        Boundable.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraPlugInfo": {
                    "implementsComputeExtent": True
                },
                "schemaTokens": {
                    "inactiveIds": {
                        "doc": """int64listop prim metadata that specifies
                the PointInstancer ids that should be masked (unrenderable)
                over all time."""
                    }
                }
            }
        })

        self.create_prop(Relationship("prototypes", metadata={
            "doc": """<b>Required property</b>. Orders and targets the prototype root 
      prims, which can be located anywhere in the scenegraph that is convenient,
      although we promote organizing prototypes as children of the 
      PointInstancer.  The position of a prototype in this relationship defines
      the value an instance would specify in the \\em protoIndices attribute to 
      instance that prototype. Since relationships are uniform, this property
      cannot be animated."""
        }))
        self.create_prop(Attribute(List[int], "protoIndices", metadata={
            "doc": """<b>Required property</b>. Per-instance index into 
      \\em prototypes relationship that identifies what geometry should be 
      drawn for each instance.  <b>Topology attribute</b> - can be animated, 
      but at a potential performance impact for streaming."""
        }))
        self.create_prop(Attribute(List[int64], "ids", metadata={
            "doc": """Ids are optional; if authored, the ids array should be the same
      length as the \\em protoIndices array, specifying (at each timeSample if
      instance identities are changing) the id of each instance. The
      type is signed intentionally, so that clients can encode some
      binary state on Id'd instances without adding a separate primvar.
      See also \\ref UsdGeomPointInstancer_varyingTopo"""
        }))
        self.create_prop(Attribute(List[point3f], "positions", metadata={
            "doc": """<b>Required property</b>. Per-instance position.  See also 
      \\ref UsdGeomPointInstancer_transform ."""
        }))
        self.create_prop(Attribute(List[quath], "orientations", metadata={
            "doc": """If authored, per-instance orientation of each instance about its 
      prototype's origin, represented as a unit length quaternion, which
      allows us to encode it with sufficient precision in a compact GfQuath.
      
      It is client's responsibility to ensure that authored quaternions are
      unit length; the convenience API below for authoring orientations from
      rotation matrices will ensure that quaternions are unit length, though
      it will not make any attempt to select the "better (for interpolation
      with respect to neighboring samples)" of the two possible quaternions
      that encode the rotation. 
      
      See also \\ref UsdGeomPointInstancer_transform ."""
        }))
        self.create_prop(Attribute(List[quatf], "orientationsf", metadata={
            "doc": """If authored, per-instance orientation of each instance about its 
      prototype's origin, represented as a unit length quaternion, encoded
      as a GfQuatf to support higher precision computations.
      
      It is client's responsibility to ensure that authored quaternions are
      unit length; the convenience API below for authoring orientations from
      rotation matrices will ensure that quaternions are unit length, though
      it will not make any attempt to select the "better (for interpolation
      with respect to neighboring samples)" of the two possible quaternions
      that encode the rotation. Note that if the earliest time sample (or
      default value if there are no time samples) of orientationsf is not empty
      orientationsf will be preferred over orientations if both are authored.
      
      See also \\ref UsdGeomPointInstancer_transform ."""
        }))
        self.create_prop(Attribute(List[float3], "scales", metadata={
            "doc": """If authored, per-instance scale to be applied to 
      each instance, before any rotation is applied.
      
      See also \\ref UsdGeomPointInstancer_transform ."""
        }))
        self.create_prop(Attribute(List[vector3f], "velocities", metadata={
            "doc": """If provided, per-instance 'velocities' will be used to 
       compute positions between samples for the 'positions' attribute,
       rather than interpolating between neighboring 'positions' samples.
       Velocities should be considered mandatory if both \\em protoIndices
       and \\em positions are animated.  Velocity is measured in position
       units per second, as per most simulation software. To convert to
       position units per UsdTimeCode, divide by
       UsdStage::GetTimeCodesPerSecond().

       See also \\ref UsdGeomPointInstancer_transform, 
       \\ref UsdGeom_VelocityInterpolation ."""
        }))
        self.create_prop(Attribute(List[vector3f], "accelerations", metadata={
            "doc": """If authored, per-instance 'accelerations' will be used with
        velocities to compute positions between samples for the 'positions'
        attribute rather than interpolating between neighboring 'positions'
        samples. Acceleration is measured in position units per second-squared.
        To convert to position units per squared UsdTimeCode, divide by the
        square of UsdStage::GetTimeCodesPerSecond()."""
        }))
        self.create_prop(Attribute(List[vector3f], "angularVelocities", metadata={
            "doc": """If authored, per-instance angular velocity vector to be used for
      interoplating orientations.  Angular velocities should be considered
      mandatory if both \\em protoIndices and \\em orientations are animated.
      Angular velocity is measured in <b>degrees</b> per second. To convert
      to degrees per UsdTimeCode, divide by
      UsdStage::GetTimeCodesPerSecond().
      
      See also \\ref UsdGeomPointInstancer_transform ."""
        }))
        self.create_prop(Attribute(List[int64], "invisibleIds", value=[], metadata={
            "doc": """A list of id's to make invisible at the evaluation time.
      See \\ref UsdGeomPointInstancer_invisibleIds ."""
        }))
