from ..attribute import Attribute
from ..dtypes import token, namespace
from ..gf import color3f, texCoord2f
from .boundable import Boundable
from typing import List


class Gprim(Boundable):
    """Base class for all geometric primitives.  
    
    Gprim encodes basic graphical properties such as \\em doubleSided and
    \\em orientation, and provides primvars for "display color" and "display
    opacity" that travel with geometry to be used as shader overrides.  """

    abstract: bool = True

    def __init__(self, name:str="")->None:
        Boundable.__init__(self, name)

        primvars = self.create_prop(Attribute(namespace, "primvars", is_leaf=False))
        primvars.create_prop(Attribute(List[color3f], "displayColor", is_leaf=True, metadata={
            "customData": {
                "apiName": "displayColor"
            },
            "doc": """It is useful to have an "official" colorSet that can be used
        as a display or modeling color, even in the absence of any specified
        shader for a gprim.  DisplayColor serves this role; because it is a
        UsdGeomPrimvar, it can also be used as a gprim override for any shader
        that consumes a \\em displayColor parameter."""
        }))
        primvars.create_prop(Attribute(List[float], "displayOpacity", is_leaf=True, metadata={
            "customData": {
                "apiName": "displayOpacity"
            },
            "doc": """Companion to \\em displayColor that specifies opacity, broken
        out as an independent attribute rather than an rgba color, both so that
        each can be independently overridden, and because shaders rarely consume
        rgba parameters."""
        }))
        primvars.create_prop(Attribute(List[texCoord2f], "st", is_leaf=True))

        self.create_prop(Attribute(bool, "doubleSided", value=False, uniform=True, metadata={
            "doc": """Although some renderers treat all parametric or polygonal
        surfaces as if they were effectively laminae with outward-facing
        normals on both sides, some renderers derive significant optimizations
        by considering these surfaces to have only a single outward side,
        typically determined by control-point winding order and/or 
        \\em orientation.  By doing so they can perform "backface culling" to
        avoid drawing the many polygons of most closed surfaces that face away
        from the viewer.
        
        However, it is often advantageous to model thin objects such as paper
        and cloth as single, open surfaces that must be viewable from both
        sides, always.  Setting a gprim's \\em doubleSided attribute to 
        \\c true instructs all renderers to disable optimizations such as
        backface culling for the gprim, and attempt (not all renderers are able
        to do so, but the USD reference GL renderer always will) to provide
        forward-facing normals on each side of the surface for lighting
        calculations."""
        }))
        self.create_prop(Attribute(token, "orientation", value="rightHanded", uniform=True, metadata={
            "allowedTokens": ["rightHanded", "leftHanded"],
            "doc": """Orientation specifies whether the gprim's surface normal 
        should be computed using the right hand rule, or the left hand rule.
        Please see \\ref UsdGeom_WindingOrder for a deeper explanation and
        generalization of orientation to composed scenes with transformation
        hierarchies."""
        }))