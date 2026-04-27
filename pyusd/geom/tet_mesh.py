from .point_based import PointBased
from ..attribute import Attribute
from ..gf import int3, int4
from typing import List


class TetMesh(PointBased):
    """Encodes a tetrahedral mesh. A tetrahedral mesh is defined as a set of 
    tetrahedra. Each tetrahedron is defined by a set of 4 points, with the 
    triangles of the tetrahedron determined from these 4 points as described in 
    the <b>tetVertexIndices</b> attribute description. The mesh surface faces 
    are encoded as triangles. Surface faces must be provided for consumers 
    that need to do surface calculations, such as renderers or consumers using 
    physics attachments. Both tetrahedra and surface face definitions use 
    indices into the TetMesh's <b>points</b> attribute, inherited from 
    UsdGeomPointBased."""
    
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
            "doc": """Flat list of the index (into the <b>points</b> attribute) of 
        each vertex of each tetrahedron in the mesh. Each int4 corresponds to the
        indices of a single tetrahedron. Users should set the <b>orientation</b>
        attribute of UsdGeomPrim accordingly. That is if the <b>orientation</b> 
        is "rightHanded", the CCW face ordering of a tetrahedron is
        [123],[032],[013],[021] with respect to the int4. This results in the
        normals facing outward from the center of the tetrahedron. The following
        diagram shows the face ordering of an unwrapped tetrahedron with 
        "rightHanded" orientation.

        \\image html USDTetMeshRightHanded.svg

        If the <b>orientation</b> attribute is set to "leftHanded" the face 
        ordering of the tetrahedron is [321],[230],[310],[120] and the 
        leftHanded CW face normals point outward from the center of the 
        tetrahedron. The following diagram shows the face ordering of an 
        unwrapped tetrahedron with "leftHanded" orientation.

        \\image html USDTetMeshLeftHanded.svg

        Setting the <b>orientation</b> attribute to align with the 
        ordering of the int4 for the tetrahedrons is the responsibility of the 
        user."""
        }))
        self.create_prop(Attribute(List[int3], "surfaceFaceVertexIndices", metadata={
            "doc": """<b>surfaceFaceVertexIndices</b> defines the triangle
        surface faces indices wrt. <b>points</b> of the tetmesh surface. Again 
        the <b>orientation</b> attribute inherited from UsdGeomPrim should be 
        set accordingly. The <b>orientation</b> for faces of tetrahedra and  
        surface faces must match."""
        }))
