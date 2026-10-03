from typing import List

from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import token
from ..gf import float3, half3, quatf
from ..typed import Typed


class SkelAnimation(Typed):
    """Describes a skel animation, where joint animation is stored in a
    vectorized form.

    See the extended \\ref UsdSkel_SkelAnimation "Skel Animation"
    documentation for more information.

    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Animation"
        }
    }

    joints: AttributeSpec[List[token]] = AttributeSpec(List[token],
        uniform=True,
        value=[],
        doc="""Array of tokens identifying which joints this animation's
        data applies to. The tokens for joints correspond to the tokens of
        Skeleton primitives. The order of the joints as listed here may
        vary from the order of joints on the Skeleton itself.
        """
    )

    translations: AttributeSpec[List[float3]] = AttributeSpec(List[float3],
        value=[],
        doc="""Joint-local translations of all affected joints. Array length
        should match the size of the *joints* attribute.
        """
    )

    rotations: AttributeSpec[List[quatf]] = AttributeSpec(List[quatf],
        value=[],
        doc="""Joint-local unit quaternion rotations of all affected joints,
        in 32-bit precision. Array length should match the size of the
        *joints* attribute.
        """
    )

    scales: AttributeSpec[List[half3]] = AttributeSpec(List[half3],
        value=[],
        doc="""Joint-local scales of all affected joints, in
        16 bit precision. Array length should match the size of the *joints*
        attribute.
        """
    )

    blendShapes: AttributeSpec[List[token]] = AttributeSpec(List[token],
        uniform=True,
        value=[],
        doc="""Array of tokens identifying which blend shapes this
        animation's data applies to. The tokens for blendShapes correspond to
        the tokens set in the *skel:blendShapes* binding property of the
        UsdSkelBindingAPI. Note that blendShapes does not accept time-sampled
        values.
        """
    )

    blendShapeWeights: AttributeSpec[List[float]] = AttributeSpec(List[float],
        value=[],
        doc="""Array of weight values for each blend shape. Each weight value
        is associated with the corresponding blend shape identified within the
        *blendShapes* token array, and therefore must have the same length as
        *blendShapes.
        """
    )
