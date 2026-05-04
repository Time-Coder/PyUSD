from .render_settings_base import RenderSettingsBase
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..relationship import Relationship
from ..common import SchemaKind


class RenderSettings(RenderSettingsBase):
    """A UsdRenderSettings prim specifies global settings for
    a render process, including an enumeration of the RenderProducts
    that should result, and the UsdGeomImageable purposes that should
    be rendered.  \\ref UsdRenderHowSettingsAffectRendering"""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Settings"
        }
    }

    class MaterialBindingPurposes(token):
        Full = "full"
        Preview = "preview"
        Empty = ""


    includedPurposes: Attribute[List[token]] = Attribute(List[token],
        uniform=True,
        doc=
        """The list of UsdGeomImageable _purpose_ values that
        should be included in the render.  Note this cannot be
        specified per-RenderProduct because it is a statement of
        which geometry is present.
        """
    )

    materialBindingPurposes: Attribute[MaterialBindingPurposes] = Attribute(MaterialBindingPurposes,
        uniform=True,
        doc=
        """Ordered list of material purposes to consider when
        resolving material bindings in the scene.  The empty string
        indicates the "allPurpose" binding.
        """
    )

    renderingColorSpace: Attribute[token] = Attribute(token,
        uniform=True,
        doc=
        """Describes a renderer's working (linear) colorSpace where all
        the renderer/shader math is expected to happen. When no
        renderingColorSpace is provided, renderer should use its own default.
        """
    )

    products: Relationship = Relationship(
        doc=
        """The set of RenderProducts the render should produce.
        This relationship should target UsdRenderProduct prims.
        If no _products_ are specified, an application should produce
        an rgb image according to the RenderSettings configuration,
        to a default display or image name.
        """
    )
