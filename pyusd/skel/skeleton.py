from typing import List

from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import token
from ..geom.boundable import Boundable
from ..gf import matrix4d


class Skeleton(Boundable):
    """Describes a skeleton.

    See the extended \\ref UsdSkel_Skeleton "Skeleton Schema" documentation for
    more information.

    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "implementsComputeExtent": True
            },
            "extraIncludes": '''
    #include "pxr/usd/usdSkel/topology.h" '''
        }
    }

    joints: AttributeSpec[List[token]] = AttributeSpec(List[token],
        uniform=True,
        value=[],
        doc="""An array of path tokens identifying the set of joints that make
        up the skeleton, and their order. Each token in the array must be valid
        when parsed as an SdfPath. The parent-child relationships of the
        corresponding paths determine the parent-child relationships of each
        joint. It is not required that the name at the end of each path be
        unique, but rather only that the paths themselves be unique.
        """
    )

    jointNames: AttributeSpec[List[token]] = AttributeSpec(List[token],
        uniform=True,
        value=[],
        doc="""If authored, provides a unique name per joint. This may be
        optionally set to provide better names when translating to DCC apps
        that require unique joint names.
        """
    )

    bindTransforms: AttributeSpec[List[matrix4d]] = AttributeSpec(List[matrix4d],
        uniform=True,
        value=[],
        doc="""Specifies the bind-pose transforms of each joint in
        **world space**, in the ordering imposed by *joints*.
        """
    )

    restTransforms: AttributeSpec[List[matrix4d]] = AttributeSpec(List[matrix4d],
        uniform=True,
        value=[],
        doc="""Specifies the rest-pose transforms of each joint in
        **local space**, in the ordering imposed by *joints*. This provides
        fallback values for joint transforms when a Skeleton either has no
        bound animation source, or when that animation source only contains
        animation for a subset of a Skeleton's joints.
        """
    )
