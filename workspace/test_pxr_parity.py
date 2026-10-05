"""Cross-check PyUSD against the reference OpenUSD implementation.

The pxr bindings live in the repo virtualenv, not on PATH, so this script
re-execs itself with `.venv\\Scripts\\python.exe` when needed.

Run with:
    python workspace/test_pxr_parity.py
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
ASSETS = Path(__file__).resolve().parent / "_assets"

FIXTURES = [
    "prims.usda",
    "sub_layer.usda",
    "layer_stack.usda",
    "variants.usda",
    "reference.usda",
    "unknown_schema.usda",
]


# A property the type declares but no layer authored still has to read as what the
# schema says it is. pxr reports the schema fallback and calls it un-authored, which is
# exactly the combination we need: a value proves the fallback is wired up, and
# HasAuthoredValue False proves emitting the default did not turn into authoring one.
#
# This is what an example under workspace/examples exercises -- def Sphere with no
# radius read as None because the generator parsed the schema defaults and then threw
# them away.
DEFAULT_FIXTURE = "HelloWorld_pyusd.usda"
# xformOpOrder is deliberately absent: it declares no default, and pyusd synthesises an
# empty list for arrays while pxr returns None there. That divergence is long-standing
# and orthogonal to a declared default, so it does not belong in this check.
DEFAULT_PRIMS = {"/hello/world": ("radius", "extent")}


def _as_comparable(value):
    """Flatten a value to nested tuples of floats so pxr and pyusd can be compared.

    pxr hands back plain tuples for a VtArray<GfVec3f> while pyusd hands back float3
    instances; the numbers are what the parity check is about.
    """
    if value is None:
        return None
    if hasattr(value, "__iter__") and not isinstance(value, str):
        return tuple(_as_comparable(item) for item in value)
    if hasattr(value, "__float__"):
        return round(float(value), 6)
    return value


def _compare_declared_defaults() -> list:
    from pxr import Usd

    from pyusd import Stage

    # The example opens this one relative to the repository root, so that is where it
    # lives; ASSETS points at workspace/_assets, which holds the parity fixtures.
    path = ROOT / "_assets" / DEFAULT_FIXTURE
    if not path.exists():
        return [f"{DEFAULT_FIXTURE}: fixture missing at {path}"]

    ours = Stage(str(path))
    theirs = Usd.Stage.Open(str(path))
    failures = []
    for prim_path, names in DEFAULT_PRIMS.items():
        our_prim = ours[prim_path]
        their_prim = theirs.GetPrimAtPath(prim_path)
        for name in names:
            their_attr = their_prim.GetAttribute(name)
            if their_attr is None:
                continue
            if their_attr.HasAuthoredValue():
                failures.append(
                    f"{prim_path}.{name}: fixture authors it, so nothing is tested"
                )
                continue

            our_value = _as_comparable(getattr(our_prim, name).get())
            their_value = _as_comparable(their_attr.Get())
            if our_value != their_value:
                failures.append(
                    f"{prim_path}.{name} declared default: "
                    f"pyusd={our_value!r} pxr={their_value!r}"
                )
                continue

            # The fallback must not count as an authored opinion.
            state = getattr(our_prim, name).value_state
            if state is not None and int(state) == 2:
                failures.append(
                    f"{prim_path}.{name}: reading the default authored an opinion"
                )
                continue

            print(f"PASS {prim_path}.{name} declared default {our_value!r}")

    return failures


def compare() -> int:
    from pxr import Usd

    from pyusd import Stage

    failures = []
    for name in FIXTURES:
        path = ASSETS / name
        if not path.exists():
            failures.append(f"{name}: fixture missing")
            continue

        ours = Stage(str(path))
        theirs = Usd.Stage.Open(str(path))

        our_paths = sorted(p.path for p in ours.traverse() if p.path != "/")
        their_paths = sorted(
            str(p.GetPath())
            for p in Usd.PrimRange(theirs.GetPseudoRoot())
            if str(p.GetPath()) != "/"
        )

        if our_paths != their_paths:
            only_ours = sorted(set(our_paths) - set(their_paths))
            only_theirs = sorted(set(their_paths) - set(our_paths))
            failures.append(
                f"{name}: prim paths differ\n"
                f"    only pyusd: {only_ours}\n"
                f"    only pxr:   {only_theirs}"
            )
            continue

        problems = []
        for prim_path in our_paths:
            our_prim = ours[prim_path]
            their_prim = theirs.GetPrimAtPath(prim_path)

            our_type = our_prim.type_name or ""
            their_type = str(their_prim.GetTypeName() or "")
            if our_type != their_type:
                problems.append(
                    f"    {prim_path} typeName: pyusd={our_type!r} pxr={their_type!r}"
                )

            # Compare the full name lists, namespaced ones included. Filtering
            # out anything with a ":" here is what let a prim hiding every
            # namespaced property pass parity: Gprim declares
            # primvars:displayColor and primvars:displayOpacity, Material declares
            # outputs:surface, Camera declares exposure:* and shutter:*, and
            # UsdPrim::GetPropertyNames reports all of them.
            our_leaf = set(our_prim.prop_names)
            their_leaf = {p.GetName() for p in their_prim.GetProperties() if p.GetName()}
            our_leaf.discard("")
            their_leaf.discard("")
            if our_leaf != their_leaf:
                problems.append(
                    f"    {prim_path} props: only pyusd={sorted(our_leaf - their_leaf)}"
                    f" only pxr={sorted(their_leaf - our_leaf)}"
                )

        if problems:
            failures.append(f"{name}:\n" + "\n".join(problems))
            continue

        print(f"PASS {name} ({len(our_paths)} prims)")

    failures.extend(_compare_namespaced_prop_names())
    failures.extend(_compare_declared_defaults())

    print()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print(f"pxr parity holds for {len(FIXTURES)} fixtures")
    return 0


# Chosen because between them they cover every kind of namespaced declaration:
# primvars:* on a Gprim, outputs:* on a Material, a legacy top-level exposure float
# beside the exposure: namespace on a Camera, and trimCurve:* on a NurbsPatch.
NAMESPACED_TYPES = ("Sphere", "Camera", "Material", "NurbsPatch")


def _compare_namespaced_prop_names() -> list:
    """Compare prop_names for types whose properties are namespaced.

    A plain Sphere used to report 8 of pxr's 10 names: prim.py filtered out every
    name containing a colon, which hid every namespaced property in the package.
    Nothing in the fixtures covered that, so it is checked directly here.
    """
    from pxr import Usd, UsdGeom, UsdShade

    from pyusd import Stage
    from pyusd.geom import Camera, NurbsPatch, Sphere
    from pyusd.shade import Material

    failures = []
    for label in NAMESPACED_TYPES:
        theirs = Usd.Stage.CreateInMemory()
        if label == "Sphere":
            UsdGeom.Sphere.Define(theirs, "/P")
            ours = Stage()
            ours.def_(Sphere, "/P")
        elif label == "Camera":
            UsdGeom.Camera.Define(theirs, "/P")
            ours = Stage()
            ours.def_(Camera, "/P")
        elif label == "Material":
            UsdShade.Material.Define(theirs, "/P")
            ours = Stage()
            ours.def_(Material, "/P")
        else:
            UsdGeom.NurbsPatch.Define(theirs, "/P")
            ours = Stage()
            ours.def_(NurbsPatch, "/P")

        mine = set(ours["/P"].prop_names)
        ref = set(theirs.GetPrimAtPath("/P").GetPropertyNames())
        if mine != ref:
            failures.append(
                f"{label} prop_names: only pyusd={sorted(mine - ref)}"
                f" only pxr={sorted(ref - mine)}"
            )
            continue

        namespaced = sorted(n for n in ref if ":" in n)
        print(f"PASS {label}.prop_names ({len(ref)} names, "
              f"namespaced: {namespaced})")

    return failures


def main() -> int:
    try:
        import pxr  # noqa: F401
    except ImportError:
        if VENV_PYTHON.exists():
            print(f"pxr missing here; re-execing {VENV_PYTHON}")
            result = subprocess.run(
                [str(VENV_PYTHON), str(Path(__file__).resolve())], cwd=str(ROOT)
            )
            return result.returncode
        print("pxr not available and no venv interpreter found")
        return 2

    return compare()


if __name__ == "__main__":
    raise SystemExit(main())
