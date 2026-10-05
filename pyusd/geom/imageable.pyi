from enum import ReprEnum

from ..attribute_spec import AttributeSpec
from ..dtypes import token
from ..relationship_spec import RelationshipSpec
from ..typed import Typed
from .visibility_api import VisibilityAPI

class Imageable(Typed):
    """Base class for all prims that may require rendering or
    visualization of some sort. The primary attributes of Imageable
    are \\em visibility and \\em purpose, which each provide instructions for
    what geometry should be included for processing by rendering and other
    computations.

    \\deprecated Imageable also provides API for accessing primvars, which
    has been moved to the UsdGeomPrimvarsAPI schema, because primvars can now
    be applied on non-Imageable prim types.  This API is planned
    to be removed, UsdGeomPrimvarsAPI should be used directly instead.
    """


    class Visibility(token, ReprEnum):
        Inherited = "inherited"
        Invisible = "invisible"

    class Purpose(token, ReprEnum):
        Default = "default"
        Render = "render"
        Proxy = "proxy"
        Guide = "guide"

    @property
    def visibility(self)->AttributeSpec[Visibility]:
        """Visibility is meant to be the simplest form of "pruning"
        visibility that is supported by most DCC apps.  Visibility is
        animatable, allowing a sub-tree of geometry to be present for some
        segment of a shot, and absent from others; unlike the action of
        deactivating geometry prims, invisible geometry is still
        available for inspection, for positioning, for defining volumes, etc."""

    @visibility.setter
    def visibility(self, value:Visibility)->None: ...

    @property
    def purpose(self)->AttributeSpec[Purpose]:
        """Purpose is a classification of geometry into categories that
        can each be independently included or excluded from traversals of prims
        on a stage, such as rendering or bounding-box computation traversals.

        See \\ref UsdGeom_ImageablePurpose for more detail about how
        \\em purpose is computed and used."""

    @purpose.setter
    def purpose(self, value:Purpose)->None: ...

    @property
    def proxyPrim(self)->RelationshipSpec:
        """The \\em proxyPrim relationship allows us to link a
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

    @proxyPrim.setter
    def proxyPrim(self, value:RelationshipSpec)->None: ...

    @property
    def visibility_api(self)->VisibilityAPI: ...
