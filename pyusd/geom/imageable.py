from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token


class Imageable(Typed):
    """Base class for all prims that may require rendering or 
    visualization of some sort. The primary attributes of Imageable 
    are \\em visibility and \\em purpose, which each provide instructions for
    what geometry should be included for processing by rendering and other
    computations.

    \\deprecated Imageable also provides API for accessing primvars, which
    has been moved to the UsdGeomPrimvarsAPI schema, because primvars can now
    be applied on non-Imageable prim types.  This API is planned
    to be removed, UsdGeomPrimvarsAPI should be used directly instead."""

    def __init__(self, name:str="")->None:
        Typed.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraIncludes": """
#include "pxr/base/gf/bbox3d.h"
#include "pxr/usd/usdGeom/primvar.h" """
            }
        })
        
        self.def_prop(Attribute(token, "visibility", value="inherited", metadata={
            "allowedTokens": ["inherited", "invisible"],
            "doc": """Visibility is meant to be the simplest form of "pruning" 
        visibility that is supported by most DCC apps.  Visibility is 
        animatable, allowing a sub-tree of geometry to be present for some 
        segment of a shot, and absent from others; unlike the action of 
        deactivating geometry prims, invisible geometry is still 
        available for inspection, for positioning, for defining volumes, etc."""
        }))

        self.def_prop(Attribute(token, "purpose", value="default", uniform=True, metadata={
            "allowedTokens": ["default", "render", "proxy", "guide"],
            "doc": """Purpose is a classification of geometry into categories that 
        can each be independently included or excluded from traversals of prims 
        on a stage, such as rendering or bounding-box computation traversals.

        See \\ref UsdGeom_ImageablePurpose for more detail about how 
        \\em purpose is computed and used.""" 
        }))

        self.def_prop(Relationship("proxyPrim", metadata={
            "doc": """The \\em proxyPrim relationship allows us to link a
        prim whose \\em purpose is "render" to its (single target)
        purpose="proxy" prim.  This is entirely optional, but can be
        useful in several scenarios:
        
        \\li In a pipeline that does pruning (for complexity management)
        by deactivating prims composed from asset references, when we
        deactivate a purpose="render" prim, we will be able to discover
        and additionally deactivate its associated purpose="proxy" prim,
        so that preview renders reflect the pruning accurately.
        
        \\li DCC importers may be able to make more aggressive optimizations
        for interactive processing and display if they can discover the proxy
        for a given render prim.
        
        \\li With a little more work, a Hydra-based application will be able
        to map a picked proxy prim back to its render geometry for selection.

        \\note It is only valid to author the proxyPrim relationship on
        prims whose purpose is "render"."""
        }))