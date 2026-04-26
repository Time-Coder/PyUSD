from .point_base import PointBased
from ..attribute import Attribute
from ..dtypes import token
from typing import List


class Mesh(PointBased):
    'Encodes a mesh with optional subdivision properties and features.\n\n    As a point-based primitive, meshes are defined in terms of points that \n    are connected into edges and faces. Many references to meshes use the\n    term \'vertex\' in place of or interchangeably with \'points\', while some\n    use \'vertex\' to refer to the \'face-vertices\' that define a face.  To\n    avoid confusion, the term \'vertex\' is intentionally avoided in favor of\n    \'points\' or \'face-vertices\'.\n\n    The connectivity between points, edges and faces is encoded using a\n    common minimal topological description of the faces of the mesh.  Each\n    face is defined by a set of face-vertices using indices into the Mesh\'s\n    _points_ array (inherited from UsdGeomPointBased) and laid out in a\n    single linear _faceVertexIndices_ array for efficiency.  A companion\n    _faceVertexCounts_ array provides, for each face, the number of\n    consecutive face-vertices in _faceVertexIndices_ that define the face.\n    No additional connectivity information is required or constructed, so\n    no adjacency or neighborhood queries are available.\n\n    A key property of this mesh schema is that it encodes both subdivision\n    surfaces and simpler polygonal meshes. This is achieved by varying the\n    _subdivisionScheme_ attribute, which is set to specify Catmull-Clark\n    subdivision by default, so polygonal meshes must always be explicitly\n    declared. The available subdivision schemes and additional subdivision\n    features encoded in optional attributes conform to the feature set of\n    OpenSubdiv\n    (https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html).\n\n    \\anchor UsdGeom_Mesh_Primvars\n    __A Note About Primvars__\n\n    The following list clarifies the number of elements for and the\n    interpolation behavior of the different primvar interpolation types\n    for meshes:\n\n    - __constant__: One element for the entire mesh; no interpolation.\n    - __uniform__: One element for each face of the mesh; elements are\n      typically not interpolated but are inherited by other faces derived\n      from a given face (via subdivision, tessellation, etc.).\n    - __varying__: One element for each point of the mesh;\n      interpolation of point data is always linear.\n    - __vertex__: One element for each point of the mesh;\n      interpolation of point data is applied according to the\n      _subdivisionScheme_ attribute.\n    - __faceVarying__: One element for each of the face-vertices that\n      define the mesh topology; interpolation of face-vertex data may\n      be smooth or linear, according to the _subdivisionScheme_ and\n      _faceVaryingLinearInterpolation_ attributes.\n\n    Primvar interpolation types and related utilities are described more\n    generally in \\ref Usd_InterpolationVals.\n\n    \\anchor UsdGeom_Mesh_Normals\n    __A Note About Normals__\n\n    Normals should not be authored on a subdivision mesh, since subdivision\n    algorithms define their own normals. They should only be authored for\n    polygonal meshes (_subdivisionScheme_ = "none").\n\n    The _normals_ attribute inherited from UsdGeomPointBased is not a generic\n    primvar, but the number of elements in this attribute will be determined by\n    its _interpolation_.  See \\ref UsdGeomPointBased::GetNormalsInterpolation() .\n    If _normals_ and _primvars:normals_ are both specified, the latter has\n    precedence.  If a polygonal mesh specifies __neither__ _normals_ nor\n    _primvars:normals_, then it should be treated and rendered as faceted,\n    with no attempt to compute smooth normals.\n\n    The normals generated for smooth subdivision schemes, e.g. Catmull-Clark\n    and Loop, will likewise be smooth, but others, e.g. Bilinear, may be\n    discontinuous between faces and/or within non-planar irregular faces.'
    def __init__(self, name = "")->None: ...

    @property
    def faceVertexIndices(self)->Attribute[List[int]]:
        'Flat list of the index (into the _points_ attribute) of each\n        vertex of each face in the mesh.  If this attribute has more than\n        one timeSample, the mesh is considered to be topologically varying.'


    @faceVertexIndices.setter
    def faceVertexIndices(self, value: List[int])->None: ...

    @property
    def faceVertexCounts(self)->Attribute[List[int]]:
        'Provides the number of vertices in each face of the mesh, \n        which is also the number of consecutive indices in _faceVertexIndices_\n        that define the face.  The length of this attribute is the number of\n        faces in the mesh.  If this attribute has more than\n        one timeSample, the mesh is considered to be topologically varying.'


    @faceVertexCounts.setter
    def faceVertexCounts(self, value: List[int])->None: ...

    @property
    def subdivisionScheme(self)->Attribute[token]:
        'The subdivision scheme to be applied to the surface.\n        Valid values are:\n\n        - __catmullClark__: The default, Catmull-Clark subdivision; preferred\n          for quad-dominant meshes (generalizes B-splines); interpolation\n          of point data is smooth (non-linear)\n        - __loop__: Loop subdivision; preferred for purely triangular meshes;\n          interpolation of point data is smooth (non-linear)\n        - __bilinear__: Subdivision reduces all faces to quads (topologically\n          similar to "catmullClark"); interpolation of point data is bilinear\n        - __none__: No subdivision, i.e. a simple polygonal mesh; interpolation\n          of point data is linear\n\n        Polygonal meshes are typically lighter weight and faster to render,\n        depending on renderer and render mode.  Use of "bilinear" will produce\n        a similar shape to a polygonal mesh and may offer additional guarantees\n        of watertightness and additional subdivision features (e.g. holes) but\n        may also not respect authored normals.'


    @subdivisionScheme.setter
    def subdivisionScheme(self, value: token)->None: ...

    @property
    def interpolateBoundary(self)->Attribute[token]:
        'Specifies how subdivision is applied for faces adjacent to\n        boundary edges and boundary points. Valid values correspond to choices\n        available in OpenSubdiv:\n\n        - __none__: No boundary interpolation is applied and boundary faces are\n          effectively treated as holes\n        - __edgeOnly__: A sequence of boundary edges defines a smooth curve to\n          which the edges of subdivided boundary faces converge\n        - __edgeAndCorner__: The default, similar to "edgeOnly" but the smooth\n          boundary curve is made sharp at corner points\n\n        These are illustrated and described in more detail in the OpenSubdiv\n        documentation:\n        https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#boundary-interpolation-rules'


    @interpolateBoundary.setter
    def interpolateBoundary(self, value: token)->None: ...

    @property
    def faceVaryingLinearInterpolation(self)->Attribute[token]:
        'Specifies how elements of a primvar of interpolation type\n        "faceVarying" are interpolated for subdivision surfaces. Interpolation\n        can be as smooth as a "vertex" primvar or constrained to be linear at\n        features specified by several options.  Valid values correspond to\n        choices available in OpenSubdiv:\n\n        - __none__: No linear constraints or sharpening, smooth everywhere\n        - __cornersOnly__: Sharpen corners of discontinuous boundaries only,\n          smooth everywhere else\n        - __cornersPlus1__: The default, same as "cornersOnly" plus additional\n          sharpening at points where three or more distinct face-varying\n          values occur\n        - __cornersPlus2__: Same as "cornersPlus1" plus additional sharpening\n          at points with at least one discontinuous boundary corner or\n          only one discontinuous boundary edge (a dart)\n        - __boundaries__: Piecewise linear along discontinuous boundaries,\n          smooth interior\n        - __all__: Piecewise linear everywhere\n\n        These are illustrated and described in more detail in the OpenSubdiv\n        documentation:\n        https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#face-varying-interpolation-rules'


    @faceVaryingLinearInterpolation.setter
    def faceVaryingLinearInterpolation(self, value: token)->None: ...

    @property
    def triangleSubdivisionRule(self)->Attribute[token]:
        'Specifies an option to the subdivision rules for the\n        Catmull-Clark scheme to try and improve undesirable artifacts when\n        subdividing triangles.  Valid values are "catmullClark" for the\n        standard rules (the default) and "smooth" for the improvement.\n\n        See https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#triangle-subdivision-rule'


    @triangleSubdivisionRule.setter
    def triangleSubdivisionRule(self, value: token)->None: ...

    @property
    def holeIndices(self)->Attribute[List[int]]:
        'The indices of all faces that should be treated as holes,\n        i.e. made invisible. This is traditionally a feature of subdivision\n        surfaces and not generally applied to polygonal meshes.'


    @holeIndices.setter
    def holeIndices(self, value: List[int])->None: ...


    @property
    def cornerIndices(self)->Attribute[List[int]]:
        'The indices of points for which a corresponding sharpness\n        value is specified in _cornerSharpnesses_ (so the size of this array\n        must match that of _cornerSharpnesses_).'


    @cornerIndices.setter
    def cornerIndices(self, value: List[int])->None: ...

    @property
    def cornerSharpnesses(self)->Attribute[List[float]]:
        'The sharpness values associated with a corresponding set of\n        points specified in _cornerIndices_ (so the size of this array must\n        match that of _cornerIndices_). Use the constant `SHARPNESS_INFINITE`\n        for a perfectly sharp corner.'


    @cornerSharpnesses.setter
    def cornerSharpnesses(self, value: List[float])->None: ...

    @property
    def creaseIndices(self)->Attribute[List[int]]:
        'The indices of points grouped into sets of successive pairs\n        that identify edges to be creased. The size of this array must be\n        equal to the sum of all elements of the _creaseLengths_ attribute.'


    @creaseIndices.setter
    def creaseIndices(self, value: List[int])->None: ...

    @property
    def creaseLengths(self)->Attribute[List[int]]:
        'The length of this array specifies the number of creases\n        (sets of adjacent sharpened edges) on the mesh. Each element gives\n        the number of points of each crease, whose indices are successively\n        laid out in the _creaseIndices_ attribute. Since each crease must\n        be at least one edge long, each element of this array must be at\n        least two.'


    @creaseLengths.setter
    def creaseLengths(self, value: List[int])->None: ...

    @property
    def creaseSharpnesses(self)->Attribute[List[float]]:
        'The per-crease or per-edge sharpness values for all creases.\n        Since _creaseLengths_ encodes the number of points in each crease,\n        the number of elements in this array will be either len(creaseLengths)\n        or the sum over all X of (creaseLengths[X] - 1). Note that while\n        the RI spec allows each crease to have either a single sharpness\n        or a value per-edge, USD will encode either a single sharpness\n        per crease on a mesh, or sharpnesses for all edges making up\n        the creases on a mesh.  Use the constant `SHARPNESS_INFINITE` for a\n        perfectly sharp crease.'


    @creaseSharpnesses.setter
    def creaseSharpnesses(self, value: List[float])->None: ...
    
