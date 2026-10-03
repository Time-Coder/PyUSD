from typing import List

from ..attribute_spec import AttributeSpec
from ..dtypes import token
from ..relationship_spec import RelationshipSpec
from .render_settings_base import RenderSettingsBase

class RenderSettings(RenderSettingsBase):
    """A UsdRenderSettings prim specifies global settings for
    a render process, including an enumeration of the RenderProducts
    that should result, and the UsdGeomImageable purposes that should
    be rendered.  \\ref UsdRenderHowSettingsAffectRendering
    """


    class MaterialBindingPurposes(token):
        Full = "full"
        Preview = "preview"
        Empty = ""

    @property
    def includedPurposes(self)->AttributeSpec[List[token]]:
        """The list of UsdGeomImageable _purpose_ values that
        should be included in the render.  Note this cannot be
        specified per-RenderProduct because it is a statement of
        which geometry is present."""

    @includedPurposes.setter
    def includedPurposes(self, value:List[token])->None: ...

    @property
    def materialBindingPurposes(self)->AttributeSpec[MaterialBindingPurposes]:
        """Ordered list of material purposes to consider when
        resolving material bindings in the scene.  The empty string
        indicates the "allPurpose" binding."""

    @materialBindingPurposes.setter
    def materialBindingPurposes(self, value:MaterialBindingPurposes)->None: ...

    @property
    def renderingColorSpace(self)->AttributeSpec[token]:
        """Describes a renderer's working (linear) colorSpace where all
        the renderer/shader math is expected to happen. When no
        renderingColorSpace is provided, renderer should use its own default."""

    @renderingColorSpace.setter
    def renderingColorSpace(self, value:token)->None: ...

    @property
    def products(self)->RelationshipSpec:
        """The set of RenderProducts the render should produce.
        This relationship should target UsdRenderProduct prims.
        If no _products_ are specified, an application should produce
        an rgb image according to the RenderSettings configuration,
        to a default display or image name."""

    @products.setter
    def products(self, value:RelationshipSpec)->None: ...
