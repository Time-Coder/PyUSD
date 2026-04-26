from .gprim import Gprim
from ..attribute import Attribute
from ..gf import point3f, vector3f, normal3f
from typing import List


class PointBase(Gprim):

    """Base class for all UsdGeomGprims that possess points,
    providing common attributes such as normals and velocities."""

    abstract: bool = True

    def __init__(self, name:str="")->None:
        Gprim.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraPlugInfo": {
                    "implementsComputeExtent": True
                }
            }
        })

        self.create_prop(Attribute(List[point3f], "points", metadata={
            "doc": """The primary geometry attribute for all PointBased
        primitives, describes points in (local) space."""
        }))
        self.create_prop(Attribute(List[vector3f], "velocities", metadata={
            "doc": """If provided, 'velocities' should be used by renderers to 

        compute positions between samples for the 'points' attribute, rather
        than interpolating between neighboring 'points' samples.  This is the
        only reasonable means of computing motion blur for topologically
        varying PointBased primitives.  It follows that the length of each
        'velocities' sample must match the length of the corresponding
        'points' sample.  Velocity is measured in position units per second,
        as per most simulation software. To convert to position units per
        UsdTimeCode, divide by UsdStage::GetTimeCodesPerSecond().
        
        See also \\ref UsdGeom_VelocityInterpolation .""" 
        }))
        self.create_prop(Attribute(List[vector3f], "accelerations", metadata={
            "doc": """If provided, 'accelerations' should be used with
        velocities to compute positions between samples for the 'points'
        attribute rather than interpolating between neighboring 'points'
        samples. Acceleration is measured in position units per second-squared.
        To convert to position units per squared UsdTimeCode, divide by the
        square of UsdStage::GetTimeCodesPerSecond()."""
        }))
        self.create_prop(Attribute(List[normal3f], "normals", metadata={
            "doc": """Provide an object-space orientation for individual points, 
        which, depending on subclass, may define a surface, curve, or free 
        points.  Note that 'normals' should not be authored on any Mesh that
        is subdivided, since the subdivision algorithm will define its own
        normals. 'normals' is not a generic primvar, but the number of elements
        in this attribute will be determined by its 'interpolation'.  See
        \\ref SetNormalsInterpolation() . If 'normals' and 'primvars:normals'
        are both specified, the latter has precedence."""
        }))