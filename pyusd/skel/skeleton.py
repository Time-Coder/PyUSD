from ..geom.boundable import Boundable
from ..attribute import Attribute
from typing import List
from ..gf import matrix4d
from ..dtypes import token
from ..common import SchemaKind


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
            "extraIncludes": """
    #include "pxr/usd/usdSkel/topology.h" """
        }
    }

    joints = Attribute(List[token],
        uniform=True,
        doc="""An array of path tokens identifying the set of joints that make
        up the skeleton, and their order. Each token in the array must be valid
        when parsed as an SdfPath. The parent-child relationships of the
        corresponding paths determine the parent-child relationships of each
        joint. It is not required that the name at the end of each path be
        unique, but rather only that the paths themselves be unique.
        """
    )

    jointNames = Attribute(List[token],
        uniform=True,
        doc="""If authored, provides a unique name per joint. This may be
        optionally set to provide better names when translating to DCC apps 
        that require unique joint names.
        """
    )

    bindTransforms = Attribute(List[matrix4d],
        uniform=True,
        doc="""Specifies the bind-pose transforms of each joint in
        **world space**, in the ordering imposed by *joints*.
        """
    )

    restTransforms = Attribute(List[matrix4d],
        uniform=True,
        doc="""Specifies the rest-pose transforms of each joint in
        **local space**, in the ordering imposed by *joints*. This provides
        fallback values for joint transforms when a Skeleton either has no
        bound animation source, or when that animation source only contains
        animation for a subset of a Skeleton's joints.
        """
    )
