from .gprim import Gprim
from ..attribute import Attribute
from ..gf import point3f, vector3f, normal3f
from typing import List


class PointBased(Gprim):
    'Base class for all UsdGeomGprims that possess points,\n    providing common attributes such as normals and velocities.'
    def __init__(self, name:str="")->None: ...

    @property
    def points(self)->Attribute[List[point3f]]:
        'The primary geometry attribute for all PointBased\n        primitives, describes points in (local) space.'


    @points.setter
    def points(self, value:List[point3f])->None: ...

    @property
    def velocities(self)->Attribute[List[vector3f]]:
        "If provided, 'velocities' should be used by renderers to \n\n        compute positions between samples for the 'points' attribute, rather\n        than interpolating between neighboring 'points' samples.  This is the\n        only reasonable means of computing motion blur for topologically\n        varying PointBased primitives.  It follows that the length of each\n        'velocities' sample must match the length of the corresponding\n        'points' sample.  Velocity is measured in position units per second,\n        as per most simulation software. To convert to position units per\n        UsdTimeCode, divide by UsdStage::GetTimeCodesPerSecond().\n        \n        See also \\ref UsdGeom_VelocityInterpolation ."


    @velocities.setter
    def velocities(self, value:List[vector3f])->None: ...

    @property
    def accelerations(self)->Attribute[List[vector3f]]:
        "If provided, 'accelerations' should be used with\n        velocities to compute positions between samples for the 'points'\n        attribute rather than interpolating between neighboring 'points'\n        samples. Acceleration is measured in position units per second-squared.\n        To convert to position units per squared UsdTimeCode, divide by the\n        square of UsdStage::GetTimeCodesPerSecond()."


    @accelerations.setter
    def accelerations(self, value:List[vector3f])->None: ...

    @property
    def normals(self)->Attribute[List[normal3f]]:
        "Provide an object-space orientation for individual points, \n        which, depending on subclass, may define a surface, curve, or free \n        points.  Note that 'normals' should not be authored on any Mesh that\n        is subdivided, since the subdivision algorithm will define its own\n        normals. 'normals' is not a generic primvar, but the number of elements\n        in this attribute will be determined by its 'interpolation'.  See\n        \\ref SetNormalsInterpolation() . If 'normals' and 'primvars:normals'\n        are both specified, the latter has precedence."


    @normals.setter
    def normals(self, value:List[normal3f])->None: ...


class PointBase(PointBased):
    pass

