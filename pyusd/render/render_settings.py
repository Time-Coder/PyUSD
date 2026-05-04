from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from typing import List
from ..dtypes import token
from ..common import SchemaKind

class RenderSettings(Typed):
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    class MaterialBindingPurposes(token):
        Full = "full"
        Preview = "preview"
        Empty = ""


    includedPurposes = Attribute(List[token],
        uniform=True,
        doc="""
The list of UsdGeomImageable _purpose_ values that
        should be included in the render.  Note this cannot be
        specified per-RenderProduct because it is a statement of
        which geometry is present.
"""
    )

    materialBindingPurposes = Attribute(MaterialBindingPurposes,
        uniform=True,
        doc="""
Ordered list of material purposes to consider when
        resolving material bindings in the scene.  The empty string
        indicates the "allPurpose" binding.
"""
    )

    renderingColorSpace = Attribute(token,
        uniform=True,
        doc="""
Describes a renderer's working (linear) colorSpace where all
        the renderer/shader math is expected to happen. When no
        renderingColorSpace is provided, renderer should use its own default.
"""
    )

    products = Relationship(
        doc="""
The set of RenderProducts the render should produce.
        This relationship should target UsdRenderProduct prims.
        If no _products_ are specified, an application should produce
        an rgb image according to the RenderSettings configuration,
        to a default display or image name.
"""
    )
