"""Regression tests for the ctypes-backed gf layer.

Every check here corresponds to a defect that type checking surfaced but the
other smoke scripts never exercised, so they would otherwise stay broken:

  * funcs.abs / min / max went through __builtins__, which is a dict inside an
    imported module, so all three raised AttributeError.
  * funcs.outerProduct called genMat.gen_type, which genMat does not define; it
    inherits genType.gen_type and needs a math_form argument.
  * genType.gen_type builds "bool3" / "matrix2b" / "quatb" module names for a
    c_bool dtype, but only the numeric vector/matrix/quat modules existed, so
    every ordering comparison and not_() raised ModuleNotFoundError.
  * funcs.not_ assigned to the class gen_type returns instead of an instance.
  * Matrix comparison walked len(self) elements while m[i] yields a row, which
    overran the result and raised IndexError.
  * genMatIterator implemented __next__ but not __iter__.
  * genMat._iop wrote the product back with self[:] = product[:], and a slice
    index matched neither branch of __setitem__, so `matrix *= matrix` silently
    left the matrix unchanged.
  * The genQuat w/x/y/z getters read `super().w`, but the ctypes field
    descriptor lives on the concrete subclass ahead of genQuat in the MRO, so
    super() never sees it and the body raised AttributeError whenever called.
  * genType._op and genType._compare_op took any operand without checking it. A
    duck-typed object that is neither a number nor a shape-matched genType was
    treated as one scalar, so `double3(...) + attribute` computed a result type
    from the attribute's delegated dtype and then assigned a whole vector into
    every element. They return NotImplemented instead, which is what lets Python
    reach the other operand's reflected method.
  * The element-wise loops in _op, _rop, _iop, _compare_op and _compare_rop all
    counted slots with len(). That is right for a flat genVec or genQuat and wrong
    for a genMat, whose __len__ is ctypes' flat element count while m[i] is a row,
    so matrix addition, subtraction and scalar multiply raised IndexError. genMat
    only rescues `*` itself, which is why multiplication worked.
  * genQuat.__init__ passed [1, 0, 0, 0] to ctypes.Structure.__init__ for the
    no-argument case. ctypes wants one positional value per field, so it raised
    "must be real number, not list" -- and since every quaternion operator
    default-constructs its result, all of quaternion arithmetic was dead.

Run with:
    python workspace/test_gf_types.py
"""

import ctypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pyusd.gf import funcs
from pyusd.gf.double3 import double3
from pyusd.gf.genMat import genMat
from pyusd.gf.genQuat import genQuat
from pyusd.gf.genVec2 import genVec2
from pyusd.gf.genVec3 import genVec3
from pyusd.gf.genVec4 import genVec4
from pyusd.gf.matrix3d import matrix3d
from pyusd.gf.matrix4d import matrix4d
from pyusd.gf.quatd import quatd

FAILURES = []


def check(label, actual, expected):
    if actual != expected:
        FAILURES.append(f"{label}: got {actual!r}, expected {expected!r}")
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
    else:
        print(f"PASS {label}")


def vec_type(cls, dtype, size):
    return cls.vec_type(dtype, size)


V2 = vec_type(genVec2, ctypes.c_float, 2)
V3 = vec_type(genVec3, ctypes.c_float, 3)
V4 = vec_type(genVec4, ctypes.c_float, 4)
M2 = genMat.mat_type(ctypes.c_double, (2, 2))
M3 = genMat.mat_type(ctypes.c_double, (3, 3))
QUAT = genQuat.quat_type(ctypes.c_double)

# --- builtins reached through the module, not through __builtins__ ----------
print("--- scalar builtins ---")
check("abs of a negative scalar", funcs.abs(-2.5), 2.5)
check("length of a negative scalar", funcs.length(-2.5), 2.5)
check("normalize of a scalar", funcs.normalize(2.0), 1.0)
check("min of two vectors", tuple(funcs.min(V3(3, 4, 0), V3(1, 1, 1))), (1.0, 1.0, 0.0))
check("max of two vectors", tuple(funcs.max(V3(3, 4, 0), V3(1, 1, 1))), (3.0, 4.0, 1.0))

# --- outerProduct needs the matrix factory, not gen_type -------------------
print()
print("--- outerProduct ---")
outer = funcs.outerProduct(V3(1, 2, 3), V3(4, 5, 6))
check("outerProduct shape", outer.shape, (3, 3))
check("outerProduct rows", [tuple(outer[i]) for i in range(3)],
      [(4.0, 5.0, 6.0), (8.0, 10.0, 12.0), (12.0, 15.0, 18.0)])

# --- bool result types have to exist ---------------------------------------
print()
print("--- vector comparisons produce bool vectors ---")
check("float2 less-than", tuple(V2(1, 2) < V2(2, 1)), (True, False))
check("float3 less-than", tuple(V3(1, 2, 3) < V3(3, 2, 1)), (True, False, False))
check("float3 greater-equal", tuple(V3(1, 2, 3) >= V3(3, 2, 1)), (False, True, True))
check("float4 less-equal", tuple(V4(1, 2, 3, 4) <= V4(4, 3, 2, 1)), (True, True, False, False))
check("scalar against vector", tuple(2.0 < V3(1, 2, 3)), (False, False, True))
check("bool3 result type", type(V3(1, 2, 3) < V3(3, 2, 1)).__name__, "bool3")
check("bool2 result type", type(V2(1, 2) < V2(2, 1)).__name__, "bool2")
check("bool4 result type", type(V4(1, 2, 3, 4) <= V4(4, 3, 2, 1)).__name__, "bool4")

# --- not_ instantiates its result -----------------------------------------
print()
print("--- not_ ---")
check("not_ of a float2", tuple(funcs.not_(V2(1, 0))), (False, True))
check("not_ of a float3", tuple(funcs.not_(V3(1, 0, 1))), (False, True, False))
check("not_ of a float4", tuple(funcs.not_(V4(0, 1, 0, 1))), (True, False, True, False))
check("not_ result type", type(funcs.not_(V3(1, 0, 1))).__name__, "bool3")

# --- matrix comparisons stay element-wise ----------------------------------
print()
print("--- matrix comparisons ---")
mat_a, mat_b = M2(), M2()
mat_a[0, 0], mat_a[1, 1] = 1.0, 5.0
mat_b[0, 0], mat_b[1, 1] = 2.0, 3.0


def as_rows(matrix):
    return [[matrix[i, j] for j in range(matrix.cols)] for i in range(matrix.rows)]


check("matrix2d less-than", as_rows(mat_a < mat_b), [[True, False], [False, False]])
check("matrix2d greater-than", as_rows(mat_a > mat_b), [[False, False], [False, True]])
check("matrix2d greater-equal", as_rows(mat_a >= mat_b), [[False, True], [True, True]])
check("scalar against matrix", as_rows(2.0 < mat_a), [[False, False], [False, True]])
check("matrix3d less-equal type", type(M3() <= M3()).__name__, "matrix3b")

# --- determinant / inverse are numeric, and *= actually writes back ---------
print()
print("--- matrix arithmetic ---")
for size, MatrixT in ((2, M2), (3, M3)):
    mat = MatrixT()
    other = MatrixT()
    for i in range(size):
        for j in range(size):
            mat.put(i, j, float((i * 3 + j * 7) % 5) + 0.5)
            other.put(i, j, float((i + j) % 4) + 1.0)

    product = mat * other
    check(f"matrix{size}d product rows",
          [product.at(i, j) for i in range(size) for j in range(size)],
          [sum(mat.at(i, k) * other.at(k, j) for k in range(size)) for i in range(size) for j in range(size)])

    expected_det = funcs.determinant(product)
    check(f"matrix{size}d determinant is a float", isinstance(expected_det, float), True)

    inverse = funcs.inverse(product)
    identity = product * inverse
    check(f"matrix{size}d M * inverse(M) is the identity",
          all(abs(identity.at(i, j) - (1.0 if i == j else 0.0)) < 1e-9
              for i in range(size) for j in range(size)),
          True)

# in-place multiply used to be a no-op because a slice index matched no branch
# of __setitem__.
diag = M2()
diag.put(0, 0, 1.0)
diag.put(1, 1, 2.0)
factor = M2()
factor.put(0, 0, 3.0)
factor.put(1, 1, 4.0)
diag *= factor
check("matrix2d *= writes back", [diag.at(i, i) for i in range(2)], [3.0, 8.0])

# --- a matrix iterator is itself iterable ---------------------------------
print()
print("--- matrix iteration ---")
matrix = M2()
iterator = iter(matrix)
check("iter of an iterator", type(iter(iterator)).__name__, "genMatIterator")
check("iter of a matrix", type(iterator).__name__, "genMatIterator")
check("rows from a matrix", len([row for row in matrix]), 2)

# --- quaternion fields come from the generated _fields_ --------------------
print()
print("--- quaternion ---")
quat = QUAT(1.0, 0.0, 0.0, 0.0)
check("quat w", quat.w, 1.0)
check("quat xyz", tuple(quat.xyz), (0.0, 0.0, 0.0))
# The ctypes field descriptor sits on the concrete subclass, ahead of genQuat in
# the MRO, so instance reads never reach these properties. Calling them directly
# used to raise AttributeError because super() cannot see the descriptor.
rich = QUAT(1.0, 2.0, 3.0, 4.0)
check("quat w getter called directly", genQuat.w.fget(rich), 1.0)
check("quat x getter called directly", genQuat.x.fget(rich), 2.0)
check("quat y getter called directly", genQuat.y.fget(rich), 3.0)
check("quat z getter called directly", genQuat.z.fget(rich), 4.0)

# An operand that is neither a number nor a shape-matched genType has to come back
# as NotImplemented, so Python falls through to the other side's reflected method
# instead of this side inventing an element-wise result out of the whole object.
check("vec op rejects a foreign operand", double3(1, 2, 3).__add__("x"), NotImplemented)
check("vec reflected op rejects a foreign operand", double3(1, 2, 3).__radd__("x"), NotImplemented)
check(
    "vec comparison rejects a foreign operand",
    double3(1, 2, 3).__gt__("x"),
    NotImplemented,
)
try:
    double3(1, 2, 3) + "x"
    check("mixing a vec with a str raises", False, True)
except TypeError:
    check("mixing a vec with a str raises", True, True)

# A genMat indexes a row at a time while __len__ is the flat element count, so the
# element-wise loops count rows. All four of these raised IndexError before.
def mat_rows(matrix):
    return [[matrix.at(i, j) for j in range(matrix.cols)] for i in range(matrix.rows)]


check("matrix + matrix", mat_rows(matrix3d() + matrix3d()), [[2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
check("matrix - matrix", mat_rows(matrix3d() - matrix3d()), [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
check("matrix * scalar", mat_rows(matrix3d() * 2), [[2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
check("4x4 matrix + 4x4 matrix", mat_rows(matrix4d() + matrix4d())[3], [0.0, 0.0, 0.0, 2.0])
scaled = matrix3d()
scaled *= 3
check("matrix *= scalar", scaled.at(1, 1), 3.0)
prod = matrix4d()
prod[0, 0] = 2.0
doubler = matrix4d()
doubler[0, 0] = 3.0
prod *= doubler
check("matrix *= matrix writes the product back", prod.at(0, 0), 6.0)
check("matrix *= matrix leaves the rest", prod.at(2, 2), 1.0)
untouched = matrix4d()
untouched *= matrix4d()
check("matrix *= identity is a no-op", untouched.at(0, 0), 1.0)

# genQuat has to default-construct, because every quaternion operator builds its
# result that way. This raised "must be real number, not list".
check("quat default construct", str(quatd()), "quatd(1.0, 0.0, 0.0, 0.0)")
identity = quatd(1.0, 0.0, 0.0, 0.0)
check("quat + quat", str(identity + identity), "quatd(2.0, 0.0, 0.0, 0.0)")
check("quat * scalar", str(identity * 2), "quatd(2.0, 0.0, 0.0, 0.0)")
check("quat * quat is the Hamilton product", str(identity * identity), "quatd(1.0, 0.0, 0.0, 0.0)")
# A half turn about X maps (x, y, z) to (x, -y, -z).
check("quat * vec rotates", str(quatd(0.0, 1.0, 0.0, 0.0) * double3(2.0, 3.0, 4.0)), "double3(2.0, -3.0, -4.0)")

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s):")
    for failure in FAILURES:
        print(f"  {failure}")
    raise SystemExit(1)

print("all gf checks passed")