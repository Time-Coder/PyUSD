from ..attribute import Attribute
from ..dtypes import namespace
from ..gf import color3f, texCoord2f

from typing import List
from typeguard import typechecked


class PrimVars(Attribute):

    @typechecked
    def __init__(self)->None:
        Attribute.__init__(self, namespace, "primvars", is_leaf=False)
        self.def_prop(Attribute(List[color3f], "displayColor", is_leaf=True, metadata={
            "customData": {
                "apiName": "displayColor"
            },
            "doc": """It is useful to have an "official" colorSet that can be used
        as a display or modeling color, even in the absence of any specified
        shader for a gprim.  DisplayColor serves this role; because it is a
        UsdGeomPrimvar, it can also be used as a gprim override for any shader
        that consumes a \\em displayColor parameter."""
        }))
        self.def_prop(Attribute(List[float], "displayOpacity", is_leaf=True, metadata={
            "customData": {
                "apiName": "displayOpacity"
            },
            "doc": """Companion to \\em displayColor that specifies opacity, broken
        out as an independent attribute rather than an rgba color, both so that
        each can be independently overridden, and because shaders rarely consume
        rgba parameters."""
        }))
        self.def_prop(Attribute(List[texCoord2f], "st", is_leaf=True))
