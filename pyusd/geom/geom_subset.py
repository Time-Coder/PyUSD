from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import token
from typing import List


class GeomSubset(Typed):
    "Encodes a subset of a piece of geometry (i.e. a UsdGeomImageable) \n    as a set of indices. Currently supports encoding subsets of faces, \n    points, edges, segments, and tetrahedrons.\n\n    To apply to a geometric prim, a GeomSubset prim must be the prim's direct \n    child in namespace, and possess a concrete defining specifier (i.e. def). \n    This restriction makes it easy and efficient to discover subsets of a prim. \n    We might want to relax this restriction if it's common to have multiple \n    <b>families</b> of subsets on a gprim and if it's useful to be able to \n    organize subsets belonging to a <b>family</b> under a common scope. See \n    'familyName' attribute for more info on defining a family of subsets.\n\n    Note that a GeomSubset isn't an imageable (i.e. doesn't derive from\n    UsdGeomImageable). So, you can't author <b>visibility</b> for it or \n    override its <b>purpose</b>.\n\n    Materials are bound to GeomSubsets just as they are for regular \n    geometry using API available in UsdShade (UsdShadeMaterial::Bind).\n"
    abstract: bool = False

    def __init__(self, name:str="")->None:
        Typed.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraIncludes": """
#include "pxr/usd/usdGeom/imageable.h"
#include "pxr/usd/usdGeom/tokens.h" """
            }
        })

        self.create_prop(Attribute(token, "elementType", value="face", metadata={
            "allowedTokens": ["face", "point", "edge", "segment", "tetrahedron"],
            "doc": """The type of geometric element indexed by this subset."""
        }))
        self.create_prop(Attribute(List[int], "indices", value=[], metadata={
            "doc": """The element indices that belong to this subset."""
        }))
        self.create_prop(Attribute(token, "familyName", value="", metadata={
            "doc": """Optional family name grouping related subsets together."""
        }))
        # DOCSYNC-BEGIN GeomSubset
        self.elementType.metadata.update({"doc": 'The type of element that the indices target. "elementType" can\n        have one of the following values:\n        <ul><li><b>face</b>: Identifies faces on a Gprim\'s surface. For a \n        UsdGeomMesh, each element of the _indices_ attribute would refer to \n        an element of the Mesh\'s _faceVertexCounts_ attribute.\n        For a UsdGeomTetMesh, each element of the _indices_ attribute would\n        refer to an element of the TetMesh\'s _surfaceFaceVertexIndices_\n        attribute.</li>\n        <li><b>point</b>: for any UsdGeomPointBased, each \n        element of the _indices_ attribute would refer to an element of the \n        Gprim\'s _points_ attribute</li>\n        <li><b>edge</b>: for any UsdGeomMesh, each pair of elements\n        in the _indices_ attribute would refer to a pair of elements of the\n        Mesh\'s _points_ attribute that are connected as an implicit edge on the\n        Mesh. These edges are derived from the Mesh\'s _faceVertexIndices_ \n        attribute. Edges are not currently defined for a UsdGeomTetMesh, but\n        could be derived from all tetrahedron edges or surface face edges only \n        if a specific use-case arises.</li>\n        <li><b>segment</b>: for any Curve, each pair of elements \n        in the _indices_ attribute would refer to a pair of indices \n        (_curveIndex_, _segmentIndex_) where _curveIndex_ is the position of \n        the specified curve in the Curve\'s _curveVertexCounts_ attribute, and \n        _segmentIndex_ is the index of the segment within that curve.</li>\n        <li><b>tetrahedron</b>: for any UsdGeomTetMesh, each element of the \n        _indices_ attribute would refer to an element of the TetMesh\'s \n        _tetVertexIndices_ attribute.\n        </li></ul>'})
        self.indices.metadata.update({"doc": 'The set of indices identifying elements included in this\n        subset. The indices need not be sorted, but the same element should not\n        be identfied more than once. Indices sampled at a given time are\n        invalid if outside the range [0, elementCount) for the elements\n        sampled from the parent geometric prim at the same time.'})
        self.familyName.metadata.update({"doc": 'The name of the family of subsets that this subset belongs to. \n        This is optional and is primarily useful when there are multiple \n        families of subsets under a geometric prim. In some cases, this could \n        also be used for achieving proper roundtripping of subset data between \n        DCC apps.\n        When multiple subsets belonging to a prim have the same familyName, they \n        are said to belong to the family. A <i>familyType</i> value can be \n        encoded on the owner of a family of subsets as a token using the static \n        method UsdGeomSubset::SetFamilyType(). "familyType" can have one of the \n        following values:\n        <ul><li><b>UsdGeomTokens->partition</b>: implies that every element of \n        the whole geometry appears exactly once in only one of the subsets\n        belonging to the family.</li>\n        <li><b>UsdGeomTokens->nonOverlapping</b>: an element that appears in one \n        subset may not appear in any other subset belonging to the family, and \n        appears only once in the subset in which it appears.</li>\n        <li><b>UsdGeomTokens->unrestricted</b>: implies that there are no\n        restrictions w.r.t. the membership of elements in the subsets. They \n        could be overlapping and the union of all subsets in the family may \n        not represent the whole.</li>\n        </ul>\n        \\note The validity of subset data is not enforced by the authoring \n        APIs, however they can be checked using UsdGeomSubset::ValidateFamily().\n        '})
        # DOCSYNC-END GeomSubset
