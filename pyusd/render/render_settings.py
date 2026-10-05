from enum import ReprEnum
from typing import List

from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import token
from ..relationship_spec import RelationshipSpec
from .render_settings_base import RenderSettingsBase


class RenderSettings(RenderSettingsBase):
    """A UsdRenderSettings prim specifies global settings for
    a render process, including an enumeration of the RenderProducts
    that should result, and the UsdGeomImageable purposes that should
    be rendered.  \\ref UsdRenderHowSettingsAffectRendering
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Settings"
        }
    }

    class MaterialBindingPurposes(token, ReprEnum):
        Full = "full"
        Preview = "preview"
        Empty = ""


    includedPurposes: AttributeSpec[List[token]] = AttributeSpec(List[token],
        uniform=True,
        value=["default", "render"],
        doc="""The list of UsdGeomImageable _purpose_ values that
        should be included in the render.  Note this cannot be
        specified per-RenderProduct because it is a statement of
        which geometry is present.
        """
    )

    materialBindingPurposes: AttributeSpec[List[MaterialBindingPurposes]] = AttributeSpec(List[MaterialBindingPurposes],
        uniform=True,
        value=["full", ""],
        doc="""Ordered list of material purposes to consider when
        resolving material bindings in the scene.  The empty string
        indicates the "allPurpose" binding.
        """
    )

    renderingColorSpace: AttributeSpec[token] = AttributeSpec(token,
        uniform=True,
        doc="""Describes a renderer's working (linear) colorSpace where all
        the renderer/shader math is expected to happen. When no
        renderingColorSpace is provided, renderer should use its own default.
        """
    )

    products = RelationshipSpec(
        doc="""The set of RenderProducts the render should produce.
        This relationship should target UsdRenderProduct prims.
        If no _products_ are specified, an application should produce
        an rgb image according to the RenderSettings configuration,
        to a default display or image name.
        """
    )
