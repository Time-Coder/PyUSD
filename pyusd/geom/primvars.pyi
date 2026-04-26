from ..attribute import Attribute
from ..gf import color3f, texCoord2f

from typing import List


class PrimVars(Attribute):

    def __init__(self)->None: ...

    @property
    def displayColor(self)->Attribute[List[color3f]]:
        """It is useful to have an "official" colorSet that can be used
        as a display or modeling color, even in the absence of any specified
        shader for a gprim.  DisplayColor serves this role; because it is a
        UsdGeomPrimvar, it can also be used as a gprim override for any shader
        that consumes a \\em displayColor parameter."""
    
    @displayColor.setter
    def displayColor(self, value: List[color3f])->None: ...

    @property
    def displayOpacity(self)->Attribute[List[float]]:
        """Companion to \\em displayColor that specifies opacity, broken
        out as an independent attribute rather than an rgba color, both so that
        each can be independently overridden, and because shaders rarely consume
        rgba parameters."""

    @displayOpacity.setter
    def displayOpacity(self, value: List[float])->None: ...

        
    @property
    def st(self)->Attribute[List[texCoord2f]]: ...

    @st.setter
    def st(self, value: List[texCoord2f])->None: ...
