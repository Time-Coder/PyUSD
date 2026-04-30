from .point_based import PointBased
from ..attribute import Attribute
from ..dtypes import token
from ..common import SchemaKind
from typing import List


class Mesh(PointBased):
    """Encodes a mesh with optional subdivision properties and features.

    As a point-based primitive, meshes are defined in terms of points that 
    are connected into edges and faces. Many references to meshes use the
    term 'vertex' in place of or interchangeably with 'points', while some
    use 'vertex' to refer to the 'face-vertices' that define a face.  To
    avoid confusion, the term 'vertex' is intentionally avoided in favor of
    'points' or 'face-vertices'.

    The connectivity between points, edges and faces is encoded using a
    common minimal topological description of the faces of the mesh.  Each
    face is defined by a set of face-vertices using indices into the Mesh's
    _points_ array (inherited from UsdGeomPointBased) and laid out in a
    single linear _faceVertexIndices_ array for efficiency.  A companion
    _faceVertexCounts_ array provides, for each face, the number of
    consecutive face-vertices in _faceVertexIndices_ that define the face.
    No additional connectivity information is required or constructed, so
    no adjacency or neighborhood queries are available.

    A key property of this mesh schema is that it encodes both subdivision
    surfaces and simpler polygonal meshes. This is achieved by varying the
    _subdivisionScheme_ attribute, which is set to specify Catmull-Clark
    subdivision by default, so polygonal meshes must always be explicitly
    declared. The available subdivision schemes and additional subdivision
    features encoded in optional attributes conform to the feature set of
    OpenSubdiv
    (https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html).

    \\anchor UsdGeom_Mesh_Primvars
    __A Note About Primvars__

    The following list clarifies the number of elements for and the
    interpolation behavior of the different primvar interpolation types
    for meshes:

    - __constant__: One element for the entire mesh; no interpolation.
    - __uniform__: One element for each face of the mesh; elements are
      typically not interpolated but are inherited by other faces derived
      from a given face (via subdivision, tessellation, etc.).
    - __varying__: One element for each point of the mesh;
      interpolation of point data is always linear.
    - __vertex__: One element for each point of the mesh;
      interpolation of point data is applied according to the
      _subdivisionScheme_ attribute.
    - __faceVarying__: One element for each of the face-vertices that
      define the mesh topology; interpolation of face-vertex data may
      be smooth or linear, according to the _subdivisionScheme_ and
      _faceVaryingLinearInterpolation_ attributes.

    Primvar interpolation types and related utilities are described more
    generally in \\ref Usd_InterpolationVals.

    \\anchor UsdGeom_Mesh_Normals
    __A Note About Normals__

    Normals should not be authored on a subdivision mesh, since subdivision
    algorithms define their own normals. They should only be authored for
    polygonal meshes (_subdivisionScheme_ = "none").

    The _normals_ attribute inherited from UsdGeomPointBased is not a generic
    primvar, but the number of elements in this attribute will be determined by
    its _interpolation_.  See \\ref UsdGeomPointBased::GetNormalsInterpolation() .
    If _normals_ and _primvars:normals_ are both specified, the latter has
    precedence.  If a polygonal mesh specifies __neither__ _normals_ nor
    _primvars:normals_, then it should be treated and rendered as faceted,
    with no attempt to compute smooth normals.

    The normals generated for smooth subdivision schemes, e.g. Catmull-Clark
    and Loop, will likewise be smooth, but others, e.g. Bilinear, may be
    discontinuous between faces and/or within non-planar irregular faces."""
    
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraIncludes": """
#include "pxr/usd/usd/timeCode.h" """
        }
    }

    faceVertexIndices: Attribute[List[int]] = Attribute(List[int], doc=
        """Flat list of the index (into the _points_ attribute) of each
        vertex of each face in the mesh.  If this attribute has more than
        one timeSample, the mesh is considered to be topologically varying."""
    )

    faceVertexCounts: Attribute[List[int]] = Attribute(List[int], doc=
        """Provides the number of vertices in each face of the mesh, 
        which is also the number of consecutive indices in _faceVertexIndices_
        that define the face.  The length of this attribute is the number of
        faces in the mesh.  If this attribute has more than
        one timeSample, the mesh is considered to be topologically varying."""
    )

    subdivisionScheme: Attribute[token] = Attribute(token, value="catmullClark", uniform=True,
        metadata={
          "allowedTokens": ["catmullClark", "loop", "bilinear", "none"]
        },
        doc="""The subdivision scheme to be applied to the surface.
        Valid values are:

        - __catmullClark__: The default, Catmull-Clark subdivision; preferred
          for quad-dominant meshes (generalizes B-splines); interpolation
          of point data is smooth (non-linear)
        - __loop__: Loop subdivision; preferred for purely triangular meshes;
          interpolation of point data is smooth (non-linear)
        - __bilinear__: Subdivision reduces all faces to quads (topologically
          similar to "catmullClark"); interpolation of point data is bilinear
        - __none__: No subdivision, i.e. a simple polygonal mesh; interpolation
          of point data is linear

        Polygonal meshes are typically lighter weight and faster to render,
        depending on renderer and render mode.  Use of "bilinear" will produce
        a similar shape to a polygonal mesh and may offer additional guarantees
        of watertightness and additional subdivision features (e.g. holes) but
        may also not respect authored normals."""
    )

    interpolateBoundary: Attribute[token] = Attribute(token, value="edgeAndCorner",
        metadata={
            "allowedTokens": ["none", "edgeOnly", "edgeAndCorner"]
        },
        doc="""Specifies how subdivision is applied for faces adjacent to
        boundary edges and boundary points. Valid values correspond to choices
        available in OpenSubdiv:

        - __none__: No boundary interpolation is applied and boundary faces are
          effectively treated as holes
        - __edgeOnly__: A sequence of boundary edges defines a smooth curve to
          which the edges of subdivided boundary faces converge
        - __edgeAndCorner__: The default, similar to "edgeOnly" but the smooth
          boundary curve is made sharp at corner points

        These are illustrated and described in more detail in the OpenSubdiv
        documentation:
        https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#boundary-interpolation-rules"""
    )

    faceVaryingLinearInterpolation: Attribute[token] = Attribute(token, value="cornersPlus1",
        metadata={
            "allowedTokens": ["none", "cornersOnly", "cornersPlus1", "cornersPlus2", "boundaries", "all"]
        },
        doc="""Specifies how elements of a primvar of interpolation type
        "faceVarying" are interpolated for subdivision surfaces. Interpolation
        can be as smooth as a "vertex" primvar or constrained to be linear at
        features specified by several options.  Valid values correspond to
        choices available in OpenSubdiv:

        - __none__: No linear constraints or sharpening, smooth everywhere
        - __cornersOnly__: Sharpen corners of discontinuous boundaries only,
          smooth everywhere else
        - __cornersPlus1__: The default, same as "cornersOnly" plus additional
          sharpening at points where three or more distinct face-varying
          values occur
        - __cornersPlus2__: Same as "cornersPlus1" plus additional sharpening
          at points with at least one discontinuous boundary corner or
          only one discontinuous boundary edge (a dart)
        - __boundaries__: Piecewise linear along discontinuous boundaries,
          smooth interior
        - __all__: Piecewise linear everywhere

        These are illustrated and described in more detail in the OpenSubdiv
        documentation:
        https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#face-varying-interpolation-rules"""
    )

    triangleSubdivisionRule: Attribute[token] = Attribute(token, value="catmullClark",
        metadata={
            "allowedTokens": ["catmullClark", "smooth"]
        },
        doc="""Specifies an option to the subdivision rules for the
        Catmull-Clark scheme to try and improve undesirable artifacts when
        subdividing triangles.  Valid values are "catmullClark" for the
        standard rules (the default) and "smooth" for the improvement.

        See https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#triangle-subdivision-rule"""
    )

    holeIndices: Attribute[List[int]] = Attribute(List[int], value=[], doc=
        """The indices of all faces that should be treated as holes,
        i.e. made invisible. This is traditionally a feature of subdivision
        surfaces and not generally applied to polygonal meshes."""
    )

    cornerIndices: Attribute[List[int]] = Attribute(List[int], value=[], doc=
        """The indices of points for which a corresponding sharpness
        value is specified in _cornerSharpnesses_ (so the size of this array
        must match that of _cornerSharpnesses_)."""
    )

    cornerSharpnesses: Attribute[List[float]] = Attribute(List[float], value=[], doc=
        """The sharpness values associated with a corresponding set of
        points specified in _cornerIndices_ (so the size of this array must
        match that of _cornerIndices_). Use the constant `SHARPNESS_INFINITE`
        for a perfectly sharp corner."""
    )

    creaseIndices: Attribute[List[int]] = Attribute(List[int], value=[], doc=
        """The indices of points grouped into sets of successive pairs
        that identify edges to be creased. The size of this array must be
        equal to the sum of all elements of the _creaseLengths_ attribute."""
    )

    creaseLengths: Attribute[List[int]] = Attribute(List[int], value=[], doc=
        """The length of this array specifies the number of creases
        (sets of adjacent sharpened edges) on the mesh. Each element gives
        the number of points of each crease, whose indices are successively
        laid out in the _creaseIndices_ attribute. Since each crease must
        be at least one edge long, each element of this array must be at
        least two."""
    )

    creaseSharpnesses: Attribute[List[float]] = Attribute(List[float], value=[], doc=
        """The per-crease or per-edge sharpness values for all creases.
        Since _creaseLengths_ encodes the number of points in each crease,
        the number of elements in this array will be either len(creaseLengths)
        or the sum over all X of (creaseLengths[X] - 1). Note that while
        the RI spec allows each crease to have either a single sharpness
        or a value per-edge, USD will encode either a single sharpness
        per crease on a mesh, or sharpnesses for all edges making up
        the creases on a mesh.  Use the constant `SHARPNESS_INFINITE` for a
        perfectly sharp crease."""
    )
