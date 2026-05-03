from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..gf import float3, quatf
from ..dtypes import token
from ..common import SchemaKind


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

    joints: Attribute[List[token]] = Attribute(List[token],
        uniform=True,
        doc=
        """Array of tokens identifying which joints this animation's
        data applies to. The tokens for joints correspond to the tokens of
        Skeleton primitives. The order of the joints as listed here may
        vary from the order of joints on the Skeleton itself.
        """
    )

    translations: Attribute[List[float3]] = Attribute(List[float3],
        doc=
        """Joint-local translations of all affected joints. Array length 
        should match the size of the *joints* attribute.
        """
    )

    rotations: Attribute[List[quatf]] = Attribute(List[quatf],
        doc=
        """Joint-local unit quaternion rotations of all affected joints, 
        in 32-bit precision. Array length should match the size of the 
        *joints* attribute.
        """
    )

    scales: Attribute[List[half3]] = Attribute(List[half3],
        doc=
        """Joint-local scales of all affected joints, in
        16 bit precision. Array length should match the size of the *joints* 
        attribute.
        """
    )

    blendShapes: Attribute[List[token]] = Attribute(List[token],
        uniform=True,
        doc=
        """Array of tokens identifying which blend shapes this
         animation's data applies to. The tokens for blendShapes correspond to
         the tokens set in the *skel:blendShapes* binding property of the
         UsdSkelBindingAPI. Note that blendShapes does not accept time-sampled
         values.
        """
    )

    blendShapeWeights: Attribute[List[float]] = Attribute(List[float],
        doc=
        """Array of weight values for each blend shape. Each weight value
        is associated with the corresponding blend shape identified within the
        *blendShapes* token array, and therefore must have the same length as
        *blendShapes.
        """
    )
