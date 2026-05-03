from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..dtypes import token
from ..gf import matrix4d
from ..relationship import Relationship
from ..common import SchemaKind


class SkelBindingAPI(APISchemaBase):
    """Provides API for authoring and extracting all the skinning-related
    data that lives in the "geometry hierarchy" of prims and models that want
    to be skeletally deformed.

    See the extended \\ref UsdSkel_BindingAPI "UsdSkelBindingAPI schema"
    documentation for more about bindings and how they apply in a scene graph.
    """
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "BindingAPI",
            "extraIncludes": """
                #include "pxr/base/tf/span.h"
                #include "pxr/usd/usdGeom/primvar.h"
                #include "pxr/usd/usdSkel/skeleton.h" """
        }
    }

    class Skinningmethod(token):
        Classiclinear = "classicLinear"
        Dualquaternion = "dualQuaternion"


    primvars: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    primvars.skel.skinningMethod = Attribute(Skinningmethod,
        uniform=True,
        value="classicLinear",
        doc="The skinningMethod specifies the skinning method for the prim.",
        metadata={
            "customData": {
                "apiName": "skinningMethod"
            }
        }
    )
    primvars.skel.geomBindTransform = Attribute(matrix4d,
        doc=
        """Encodes the bind-time world space transforms of the prim.
        If the transform is identical for a group of gprims that share a common
        ancestor, the transform may be authored on the ancestor, to "inherit"
        down to all the leaf gprims. If this transform is unset, an identity
        transform is used instead.
        """,
        metadata={
            "customData": {
                "apiName": "geomBindTransform"
            }
        }
    )
    primvars.skel.jointIndices = Attribute(List[int],
        doc=
        """Indices into the *joints* attribute of the closest
        (in namespace) bound Skeleton that affect each point of a PointBased
        gprim. The primvar can have either *constant* or *vertex* interpolation.
        This primvar's *elementSize* will determine how many joint influences
        apply to each point. Indices must point be valid. Null influences should
        be defined by setting values in jointWeights to zero.
        See UsdGeomPrimvar for more information on interpolation and
        elementSize.
        """,
        metadata={
            "customData": {
                "apiName": "jointIndices"
            }
        }
    )
    primvars.skel.jointWeights = Attribute(List[float],
        doc=
        """Weights for the joints that affect each point of a PointBased
        gprim. The primvar can have either *constant* or *vertex* interpolation.
        This primvar's *elementSize* will determine how many joints influences
        apply to each point. The length, interpolation, and elementSize of
        *jointWeights* must match that of *jointIndices*. See UsdGeomPrimvar
        for more information on interpolation and elementSize.
        """,
        metadata={
            "customData": {
                "apiName": "jointWeights"
            }
        }
    )

    skel: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    skel.joints = Attribute(List[token],
        uniform=True,
        doc=
        """An (optional) array of tokens defining the list of
        joints to which jointIndices apply. If not defined, jointIndices applies
        to the ordered list of joints defined in the bound Skeleton's *joints*
        attribute. If undefined on a primitive, the primitive inherits the 
        value of the nearest ancestor prim, if any.
        """,
        metadata={
            "customData": {
                "apiName": "joints"
            }
        }
    )
    skel.blendShapes = Attribute(List[token],
        uniform=True,
        doc=
        """An array of tokens defining the order onto which blend shape
        weights from an animation source map onto the *skel:blendShapeTargets*
        rel of a binding site. If authored, the number of elements must be equal
        to the number of targets in the _blendShapeTargets_ rel. This property
        is not inherited hierarchically, and is expected to be authored directly
        on the skinnable primitive to which the blend shapes apply.
        """,
        metadata={
            "customData": {
                "apiName": "blendShapes"
            }
        }
    )

    animationSource: Relationship = Relationship(
        doc=
        """Animation source to be bound to Skeleton primitives at or
        beneath the location at which this property is defined.
        
        """,
        metadata={
            "customData": {
                "apiName": "animationSource"
            }
        }
    )

    skeleton: Relationship = Relationship(
        doc=
        """Skeleton to be bound to this prim and its descendents that
        possess a mapping and weighting to the joints of the identified
        Skeleton.
        """,
        metadata={
            "customData": {
                "apiName": "skeleton"
            }
        }
    )

    blendShapeTargets: Relationship = Relationship(
        doc=
        """Ordered list of all target blend shapes. This property is not
        inherited hierarchically, and is expected to be authored directly on
        the skinnable primitive to which the the blend shapes apply.
        """,
        metadata={
            "customData": {
                "apiName": "blendShapeTargets"
            }
        }
    )
