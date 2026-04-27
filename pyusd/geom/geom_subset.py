from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import token
from typing import List


class GeomSubset(Typed):
    """Encodes a subset of a piece of geometry (i.e. a UsdGeomImageable) 
    as a set of indices. Currently supports encoding subsets of faces, 
    points, edges, segments, and tetrahedrons.

    To apply to a geometric prim, a GeomSubset prim must be the prim's direct 
    child in namespace, and possess a concrete defining specifier (i.e. def). 
    This restriction makes it easy and efficient to discover subsets of a prim. 
    We might want to relax this restriction if it's common to have multiple 
    <b>families</b> of subsets on a gprim and if it's useful to be able to 
    organize subsets belonging to a <b>family</b> under a common scope. See 
    'familyName' attribute for more info on defining a family of subsets.

    Note that a GeomSubset isn't an imageable (i.e. doesn't derive from
    UsdGeomImageable). So, you can't author <b>visibility</b> for it or 
    override its <b>purpose</b>.

    Materials are bound to GeomSubsets just as they are for regular 
    geometry using API available in UsdShade (UsdShadeMaterial::Bind).
"""

    abstract: bool = False

    def __init__(self, name:str="")->None:
        Typed.__init__(self, name)

        self.metadata.update({
            "customData": {
                "className": "Subset",
                "extraIncludes": """
#include "pxr/base/tf/token.h"
#include "pxr/usd/usdGeom/imageable.h"
#include "pxr/usd/usdGeom/mesh.h"
#include "pxr/usd/usdGeom/tetMesh.h"
#include "pxr/usd/usdGeom/basisCurves.h"
"""
            }
        })

        self.create_prop(Attribute(token, "elementType", value="face", uniform=True, metadata={
            "allowedTokens": ["face", "point", "edge", "segment", "tetrahedron"],
            "doc": """The type of element that the indices target. "elementType" can
        have one of the following values:
        <ul><li><b>face</b>: Identifies faces on a Gprim's surface. For a 
        UsdGeomMesh, each element of the _indices_ attribute would refer to 
        an element of the Mesh's _faceVertexCounts_ attribute.
        For a UsdGeomTetMesh, each element of the _indices_ attribute would
        refer to an element of the TetMesh's _surfaceFaceVertexIndices_
        attribute.</li>
        <li><b>point</b>: for any UsdGeomPointBased, each 
        element of the _indices_ attribute would refer to an element of the 
        Gprim's _points_ attribute</li>
        <li><b>edge</b>: for any UsdGeomMesh, each pair of elements
        in the _indices_ attribute would refer to a pair of elements of the
        Mesh's _points_ attribute that are connected as an implicit edge on the
        Mesh. These edges are derived from the Mesh's _faceVertexIndices_ 
        attribute. Edges are not currently defined for a UsdGeomTetMesh, but
        could be derived from all tetrahedron edges or surface face edges only 
        if a specific use-case arises.</li>
        <li><b>segment</b>: for any Curve, each pair of elements 
        in the _indices_ attribute would refer to a pair of indices 
        (_curveIndex_, _segmentIndex_) where _curveIndex_ is the position of 
        the specified curve in the Curve's _curveVertexCounts_ attribute, and 
        _segmentIndex_ is the index of the segment within that curve.</li>
        <li><b>tetrahedron</b>: for any UsdGeomTetMesh, each element of the 
        _indices_ attribute would refer to an element of the TetMesh's 
        _tetVertexIndices_ attribute.
        </li></ul>"""
        }))
        self.create_prop(Attribute(List[int], "indices", value=[], metadata={
            "doc": """The set of indices identifying elements included in this
        subset. The indices need not be sorted, but the same element should not
        be identfied more than once. Indices sampled at a given time are
        invalid if outside the range [0, elementCount) for the elements
        sampled from the parent geometric prim at the same time."""
        }))
        self.create_prop(Attribute(token, "familyName", value="", uniform=True, metadata={
            "doc": """The name of the family of subsets that this subset belongs to. 
        This is optional and is primarily useful when there are multiple 
        families of subsets under a geometric prim. In some cases, this could 
        also be used for achieving proper roundtripping of subset data between 
        DCC apps.
        When multiple subsets belonging to a prim have the same familyName, they 
        are said to belong to the family. A <i>familyType</i> value can be 
        encoded on the owner of a family of subsets as a token using the static 
        method UsdGeomSubset::SetFamilyType(). "familyType" can have one of the 
        following values:
        <ul><li><b>UsdGeomTokens->partition</b>: implies that every element of 
        the whole geometry appears exactly once in only one of the subsets
        belonging to the family.</li>
        <li><b>UsdGeomTokens->nonOverlapping</b>: an element that appears in one 
        subset may not appear in any other subset belonging to the family, and 
        appears only once in the subset in which it appears.</li>
        <li><b>UsdGeomTokens->unrestricted</b>: implies that there are no
        restrictions w.r.t. the membership of elements in the subsets. They 
        could be overlapping and the union of all subsets in the family may 
        not represent the whole.</li>
        </ul>
        \\note The validity of subset data is not enforced by the authoring 
        APIs, however they can be checked using UsdGeomSubset::ValidateFamily().
        """
        }))
