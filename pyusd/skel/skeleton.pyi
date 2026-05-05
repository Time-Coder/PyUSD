from ..geom.boundable import Boundable
from ..gf import matrix4d
from ..dtypes import token
from .primvars import Primvars
from .skel import Skel


class Skeleton(Boundable):
    """Describes a skeleton. 
    
    See the extended \\ref UsdSkel_Skeleton "Skeleton Schema" documentation for
    more information.
    
    """

    @property
    def joints(self)->Attribute[List[token]]:
        """An array of path tokens identifying the set of joints that make
        up the skeleton, and their order. Each token in the array must be valid
        when parsed as an SdfPath. The parent-child relationships of the
        corresponding paths determine the parent-child relationships of each
        joint. It is not required that the name at the end of each path be
        unique, but rather only that the paths themselves be unique."""

    @joints.setter
    def joints(self, value:List[token])->None: ...

    @property
    def jointNames(self)->Attribute[List[token]]:
        """If authored, provides a unique name per joint. This may be
        optionally set to provide better names when translating to DCC apps 
        that require unique joint names."""

    @jointNames.setter
    def jointNames(self, value:List[token])->None: ...

    @property
    def bindTransforms(self)->Attribute[List[matrix4d]]:
        """Specifies the bind-pose transforms of each joint in
        **world space**, in the ordering imposed by *joints*."""

    @bindTransforms.setter
    def bindTransforms(self, value:List[matrix4d])->None: ...

    @property
    def restTransforms(self)->Attribute[List[matrix4d]]:
        """Specifies the rest-pose transforms of each joint in
        **local space**, in the ordering imposed by *joints*. This provides
        fallback values for joint transforms when a Skeleton either has no
        bound animation source, or when that animation source only contains
        animation for a subset of a Skeleton's joints."""

    @restTransforms.setter
    def restTransforms(self, value:List[matrix4d])->None: ...

