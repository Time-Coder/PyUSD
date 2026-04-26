from ..prim import Prim
from ..attribute import Attribute
from ..dtypes import token
from ..api_schema_base import APISchemaBase


class VisibilityAPI(APISchemaBase):
    '\n    UsdGeomVisibilityAPI introduces properties that can be used to author\n    visibility opinions.\n   \n    \\note\n    Currently, this schema only introduces the attributes that are used to\n    control purpose visibility. Later, this schema will define _all_\n    visibility-related properties and UsdGeomImageable will no longer define\n    those properties.\n   \n    The purpose visibility attributes added by this schema,\n    _guideVisibility_, _proxyVisibility_, and _renderVisibility_ can each be\n    used to control visibility for geometry of the corresponding purpose\n    values, with the overall _visibility_ attribute acting as an\n    override. I.e., if _visibility_ evaluates to "invisible", purpose\n    visibility is invisible; otherwise, purpose visibility is determined by\n    the corresponding purpose visibility attribute.\n\n    Note that the behavior of _guideVisibility_ is subtly different from the\n    _proxyVisibility_ and _renderVisibility_ attributes, in that "guide"\n    purpose visibility always evaluates to either "invisible" or "visible",\n    whereas the other attributes may yield computed values of "inherited" if\n    there is no authored opinion on the attribute or inherited from an\n    ancestor. This is motivated by the fact that, in Pixar"s user workflows,\n    we have never found a need to have all guides visible in a scene by\n    default, whereas we do find that flexibility useful for "proxy" and\n    "render" geometry.\n\n    This schema can only be applied to UsdGeomImageable prims. The\n    UseGeomImageable schema provides API for computing the purpose visibility\n    values that result from the attributes introduced by this schema.\n    '
    @classmethod
    def apply(cls, prim:Prim)->Prim:
        prim.metadata.apiSchemas.append(cls.__name__)
        prim.create_prop(Attribute(token, "guideVisibility", value="invisible", uniform=True, metadata={
            "allowedTokens": ["inherited", "invisible", "visible"],
            "doc": """This attribute controls visibility for geometry with purpose
        "guide"."""
        }))
        prim.create_prop(Attribute(token, "proxyVisibility", value="inherited", uniform=True, metadata={
            "allowedTokens": ["inherited", "invisible", "visible"],
            "doc": """This attribute controls visibility for geometry with purpose
        "proxy"."""
        }))
        prim.create_prop(Attribute(token, "renderVisibility", value="inherited", uniform=True, metadata={
            "allowedTokens": ["inherited", "invisible", "visible"],
            "doc": """This attribute controls visibility for geometry with purpose
        "render"."""
        }))
        # DOCSYNC-BEGIN VisibilityAPI
        prim.guideVisibility.metadata.update({"doc": '\n        This attribute controls visibility for geometry with purpose "guide".\n\n        Unlike overall _visibility_, _guideVisibility_ is uniform, and\n        therefore cannot be animated.\n\n        Also unlike overall _visibility_, _guideVisibility_ is tri-state, in\n        that a descendant with an opinion of "visible" overrides an ancestor\n        opinion of "invisible".\n\n        The _guideVisibility_ attribute works in concert with the overall\n        _visibility_ attribute: The visibility of a prim with purpose "guide"\n        is determined by the inherited values it receives for the _visibility_\n        and _guideVisibility_ attributes. If _visibility_ evaluates to\n        "invisible", the prim is invisible. If _visibility_ evaluates to\n        "inherited" and _guideVisibility_ evaluates to "visible", then the\n        prim is visible. __Otherwise, it is invisible.__\n        '})
        prim.proxyVisibility.metadata.update({"doc": '\n        This attribute controls visibility for geometry with purpose "proxy".\n\n        Unlike overall _visibility_, _proxyVisibility_ is uniform, and\n        therefore cannot be animated.\n\n        Also unlike overall _visibility_, _proxyVisibility_ is tri-state, in\n        that a descendant with an opinion of "visible" overrides an ancestor\n        opinion of "invisible".\n\n        The _proxyVisibility_ attribute works in concert with the overall\n        _visibility_ attribute: The visibility of a prim with purpose "proxy"\n        is determined by the inherited values it receives for the _visibility_\n        and _proxyVisibility_ attributes. If _visibility_ evaluates to\n        "invisible", the prim is invisible. If _visibility_ evaluates to\n        "inherited" then: If _proxyVisibility_ evaluates to "visible", then\n        the prim is visible; if _proxyVisibility_ evaluates to "invisible",\n        then the prim is invisible; if _proxyVisibility_ evaluates to\n        "inherited", then the prim may either be visible or invisible,\n        depending on a fallback value determined by the calling context.\n        '})
        prim.renderVisibility.metadata.update({"doc": '\n        This attribute controls visibility for geometry with purpose\n        "render".\n\n        Unlike overall _visibility_, _renderVisibility_ is uniform, and\n        therefore cannot be animated.\n\n        Also unlike overall _visibility_, _renderVisibility_ is tri-state, in\n        that a descendant with an opinion of "visible" overrides an ancestor\n        opinion of "invisible".\n\n        The _renderVisibility_ attribute works in concert with the overall\n        _visibility_ attribute: The visibility of a prim with purpose "render"\n        is determined by the inherited values it receives for the _visibility_\n        and _renderVisibility_ attributes. If _visibility_ evaluates to\n        "invisible", the prim is invisible. If _visibility_ evaluates to\n        "inherited" then: If _renderVisibility_ evaluates to "visible", then\n        the prim is visible; if _renderVisibility_ evaluates to "invisible",\n        then the prim is invisible; if _renderVisibility_ evaluates to\n        "inherited", then the prim may either be visible or invisible,\n        depending on a fallback value determined by the calling context.\n        '})
        # DOCSYNC-END VisibilityAPI
        return prim
