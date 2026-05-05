from ..typed import Typed
from ..gf import float3, quatf
from ..dtypes import token
from .primvars import Primvars
from .skel import Skel


class SkelAnimation(Typed):
    """Describes a skel animation, where joint animation is stored in a
    vectorized form.
    
    See the extended \\ref UsdSkel_SkelAnimation "Skel Animation"
    documentation for more information.
    
    """

    @property
    def joints(self)->Attribute[List[token]]:
        """Array of tokens identifying which joints this animation's
        data applies to. The tokens for joints correspond to the tokens of
        Skeleton primitives. The order of the joints as listed here may
        vary from the order of joints on the Skeleton itself."""

    @joints.setter
    def joints(self, value:List[token])->None: ...

    @property
    def translations(self)->Attribute[List[float3]]:
        """Joint-local translations of all affected joints. Array length 
        should match the size of the *joints* attribute."""

    @translations.setter
    def translations(self, value:List[float3])->None: ...

    @property
    def rotations(self)->Attribute[List[quatf]]:
        """Joint-local unit quaternion rotations of all affected joints, 
        in 32-bit precision. Array length should match the size of the 
        *joints* attribute."""

    @rotations.setter
    def rotations(self, value:List[quatf])->None: ...

    @property
    def scales(self)->Attribute[List[half3]]:
        """Joint-local scales of all affected joints, in
        16 bit precision. Array length should match the size of the *joints* 
        attribute."""

    @scales.setter
    def scales(self, value:List[half3])->None: ...

    @property
    def blendShapes(self)->Attribute[List[token]]:
        """Array of tokens identifying which blend shapes this
         animation's data applies to. The tokens for blendShapes correspond to
         the tokens set in the *skel:blendShapes* binding property of the
         UsdSkelBindingAPI. Note that blendShapes does not accept time-sampled
         values."""

    @blendShapes.setter
    def blendShapes(self, value:List[token])->None: ...

    @property
    def blendShapeWeights(self)->Attribute[List[float]]:
        """Array of weight values for each blend shape. Each weight value
        is associated with the corresponding blend shape identified within the
        *blendShapes* token array, and therefore must have the same length as
        *blendShapes."""

    @blendShapeWeights.setter
    def blendShapeWeights(self, value:List[float])->None: ...

