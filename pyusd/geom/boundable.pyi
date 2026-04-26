from .xformable import Xformable
from ..attribute import Attribute
from ..gf import float3
from typing import List


class Boundable(Xformable):
    """Boundable introduces the ability for a prim to persistently
    cache a rectilinear, local-space, extent.
    
    \\section UsdGeom_Boundable_Extent Why Extent and not Bounds ?
    Boundable introduces the notion of "extent", which is a cached computation
    of a prim's local-space 3D range for its resolved attributes <b>at the
    layer and time in which extent is authored</b>.  We have found that with
    composed scene description, attempting to cache pre-computed bounds at
    interior prims in a scene graph is very fragile, given the ease with which
    one can author a single attribute in a stronger layer that can invalidate
    many authored caches - or with which a re-published, referenced asset can
    do the same.
    
    Therefore, we limit to precomputing (generally) leaf-prim extent, which
    avoids the need to read in large point arrays to compute bounds, and
    provides UsdGeomBBoxCache the means to efficiently compute and
    (session-only) cache intermediate bounds.  You are free to compute and
    author intermediate bounds into your scenes, of course, which may work
    well if you have sufficient locks on your pipeline to guarantee that once
    authored, the geometry and transforms upon which they are based will
    remain unchanged, or if accuracy of the bounds is not an ironclad
    requisite. 
    
    When intermediate bounds are authored on Boundable parents, the child prims
    will be pruned from BBox computation; the authored extent is expected to
    incorporate all child bounds."""

    def __init__(self, name:str="")->None: ...

    @property
    def extent(self)->Attribute[List[float3]]:
        """Extent is a three dimensional range measuring the geometric
        extent of the authored gprim in its own local space (i.e. its own
        transform not applied), \\em without accounting for any shader-induced
        displacement. If __any__ extent value has been authored for a given 
        Boundable, then it should be authored at every timeSample at which 
        geometry-affecting properties are authored, to ensure correct 
        evaluation via ComputeExtent(). If __no__ extent value has been 
        authored, then ComputeExtent() will call the Boundable's registered 
        ComputeExtentFunction(), which may be expensive, which is why we 
        strongly encourage proper authoring of extent.
        \\sa ComputeExtent()
        \\sa \\ref UsdGeom_Boundable_Extent.
        
        An authored extent on a prim which has children is expected to include
        the extent of all children, as they will be pruned from BBox computation
        during traversal."""

    @extent.setter
    def extent(self, value:List[float3])->None: ...