from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..gf import vector3f
from ..common import SchemaKind


class BlendShape(Typed):
    """Describes a target blend shape, possibly containing inbetween
      shapes.

      See the extended \\ref UsdSkel_BlendShape "Blend Shape Schema
      documentation for information.
      """
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraIncludes": """
                #include "pxr/base/tf/span.h"
                #include "pxr/usd/usdSkel/inbetweenShape.h" """
        }
    }

    offsets: Attribute[List[vector3f]] = Attribute(List[vector3f],
        uniform=True,
        doc=
        """**Required property**. Position offsets which, when added to the
        base pose, provides the target shape.
        """
    )

    normalOffsets: Attribute[List[vector3f]] = Attribute(List[vector3f],
        uniform=True,
        doc=
        """**Required property**. Normal offsets which, when added to the
        base pose, provides the normals of the target shape.
        """
    )

    pointIndices: Attribute[List[int]] = Attribute(List[int],
        uniform=True,
        doc=
        """**Optional property**. Indices into the original mesh that
        correspond to the values in *offsets* and of any inbetween shapes. If
        authored, the number of elements must be equal to the number of elements
        in the *offsets* array.
        """
    )
