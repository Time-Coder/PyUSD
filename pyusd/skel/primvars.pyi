from typing import List

from ..attribute_spec import AttributeSpec
from ..dtypes import token
from ..gf import matrix4d

class Primvars(AttributeSpec):

    class SkinningMethod(token):
        ClassicLinear = "classicLinear"
        DualQuaternion = "dualQuaternion"


    @property
    def skinningMethod(self)->AttributeSpec[SkinningMethod]:
        """The skinningMethod specifies the skinning method for the prim."""

    @skinningMethod.setter
    def skinningMethod(self, value:SkinningMethod)->None: ...

    @property
    def geomBindTransform(self)->AttributeSpec[matrix4d]:
        """Encodes the bind-time world space transforms of the prim.
        If the transform is identical for a group of gprims that share a common
        ancestor, the transform may be authored on the ancestor, to "inherit"
        down to all the leaf gprims. If this transform is unset, an identity
        transform is used instead."""

    @geomBindTransform.setter
    def geomBindTransform(self, value:matrix4d)->None: ...

    @property
    def jointIndices(self)->AttributeSpec[List[int]]:
        """Indices into the *joints* attribute of the closest
        (in namespace) bound Skeleton that affect each point of a PointBased
        gprim. The primvar can have either *constant* or *vertex* interpolation.
        This primvar's *elementSize* will determine how many joint influences
        apply to each point. Indices must point be valid. Null influences should
        be defined by setting values in jointWeights to zero.
        See UsdGeomPrimvar for more information on interpolation and
        elementSize."""

    @jointIndices.setter
    def jointIndices(self, value:List[int])->None: ...

    @property
    def jointWeights(self)->AttributeSpec[List[float]]:
        """Weights for the joints that affect each point of a PointBased
        gprim. The primvar can have either *constant* or *vertex* interpolation.
        This primvar's *elementSize* will determine how many joints influences
        apply to each point. The length, interpolation, and elementSize of
        *jointWeights* must match that of *jointIndices*. See UsdGeomPrimvar
        for more information on interpolation and elementSize."""

    @jointWeights.setter
    def jointWeights(self, value:List[float])->None: ...
