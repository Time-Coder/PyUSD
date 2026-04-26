from ..attribute import Attribute
from .boundable import Boundable
from .primvars import PrimVars
from ..dtypes import token


class Gprim(Boundable):
    """Base class for all geometric primitives.  
    
    Gprim encodes basic graphical properties such as \\em doubleSided and
    \\em orientation, and provides primvars for "display color" and "display
    opacity" that travel with geometry to be used as shader overrides.  """

    def __init__(self, name:str="")->None: ...

    @property
    def primvars(self) -> PrimVars: ...

    @property
    def doubleSided(self) -> Attribute[bool]:
        """Although some renderers treat all parametric or polygonal
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

    @doubleSided.setter
    def doubleSided(self, value:bool) -> None: ...

    @property
    def orientation(self) -> Attribute[token]:
        """Orientation specifies whether the gprim's surface normal 
        should be computed using the right hand rule, or the left hand rule.
        Please see \\ref UsdGeom_WindingOrder for a deeper explanation and
        generalization of orientation to composed scenes with transformation
        hierarchies."""

    @orientation.setter
    def orientation(self, value:token) -> None: ...