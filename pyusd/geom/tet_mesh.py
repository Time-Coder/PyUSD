from .point_base import PointBased
from ..attribute import Attribute
from ..gf import int3, int4
from typing import List


class TetMesh(PointBased):
    "Encodes a tetrahedral mesh. A tetrahedral mesh is defined as a set of \n    tetrahedra. Each tetrahedron is defined by a set of 4 points, with the \n    triangles of the tetrahedron determined from these 4 points as described in \n    the <b>tetVertexIndices</b> attribute description. The mesh surface faces \n    are encoded as triangles. Surface faces must be provided for consumers \n    that need to do surface calculations, such as renderers or consumers using \n    physics attachments. Both tetrahedra and surface face definitions use \n    indices into the TetMesh's <b>points</b> attribute, inherited from \n    UsdGeomPointBased."
    abstract: bool = False

    def __init__(self, name:str="")->None:
        PointBased.__init__(self, name)

        self.metadata.update({
            "customData": {
                "extraIncludes": """
#include "pxr/usd/usd/timeCode.h" """
            }
        })

        self.create_prop(Attribute(List[int4], "tetVertexIndices", metadata={
            "doc": """Indices of the four vertices that define each tetrahedron."""
        }))
        self.create_prop(Attribute(List[int3], "surfaceFaceVertexIndices", metadata={
            "doc": """Triangle indices describing the boundary surface of the tet mesh."""
        }))
        # DOCSYNC-BEGIN TetMesh
        self.tetVertexIndices.metadata.update({"doc": 'Flat list of the index (into the <b>points</b> attribute) of \n        each vertex of each tetrahedron in the mesh. Each int4 corresponds to the\n        indices of a single tetrahedron. Users should set the <b>orientation</b>\n        attribute of UsdGeomPrim accordingly. That is if the <b>orientation</b> \n        is "rightHanded", the CCW face ordering of a tetrahedron is\n        [123],[032],[013],[021] with respect to the int4. This results in the\n        normals facing outward from the center of the tetrahedron. The following\n        diagram shows the face ordering of an unwrapped tetrahedron with \n        "rightHanded" orientation.\n\n        \\image html USDTetMeshRightHanded.svg\n\n        If the <b>orientation</b> attribute is set to "leftHanded" the face \n        ordering of the tetrahedron is [321],[230],[310],[120] and the \n        leftHanded CW face normals point outward from the center of the \n        tetrahedron. The following diagram shows the face ordering of an \n        unwrapped tetrahedron with "leftHanded" orientation.\n\n        \\image html USDTetMeshLeftHanded.svg\n\n        Setting the <b>orientation</b> attribute to align with the \n        ordering of the int4 for the tetrahedrons is the responsibility of the \n        user.'})
        self.surfaceFaceVertexIndices.metadata.update({"doc": '<b>surfaceFaceVertexIndices</b> defines the triangle\n        surface faces indices wrt. <b>points</b> of the tetmesh surface. Again \n        the <b>orientation</b> attribute inherited from UsdGeomPrim should be \n        set accordingly. The <b>orientation</b> for faces of tetrahedra and  \n        surface faces must match.'})
        # DOCSYNC-END TetMesh
