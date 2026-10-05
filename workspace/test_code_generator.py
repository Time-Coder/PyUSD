"""Regression tests for the schema code generator.

Every check here corresponds to a defect that made `generate_all` produce a tree
that would not import or would lose behaviour. They are cheap and direct: the
generator is asked for the text of one class, and the text is inspected.

The broader question -- whether a full regeneration still yields a working
package -- is answered by regenerating into a scratch tree and running the
workspace suite against it, which is what stage 1 of the Property/AttributeSpec
split had to establish before any generated file could be rewritten.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pyusd.code_generator import CodeGenerator

FAILURES = []


def check(label, actual, expected):
    if actual != expected:
        FAILURES.append(f"{label}: got {actual!r}, expected {expected!r}")


def check_true(label, actual):
    check(label, bool(actual), True)


def geom_generator():
    generator = CodeGenerator("pyusd/geom/schema.usda")
    generator.parse()
    return generator


def body_of(generator, class_name):
    return generator._generate_class_definition(generator.classes_info[class_name])


# --- a leaf attribute is a plain annotated assignment -----------------------
# It used to be emitted as `name.create_prop(...)` when the attribute's name
# collided with a member of Attribute. create_prop is an instance method that
# registers a child on an existing property object, and a leaf name is not such
# an object, so the generated module raised NameError on import.
def test_leaf_attribute_is_assigned_not_created() -> None:
    generator = geom_generator()
    color_space = CodeGenerator("pyusd/schema.usda")
    color_space.parse()
    body = color_space._generate_class_definition(
        color_space.classes_info["ColorSpaceDefinitionAPI"]
    )

    check_true(
        "reserved attribute name is assigned",
        "name: AttributeSpec[token] = AttributeSpec(token," in body,
    )
    check_true(
        "reserved attribute name is not created via create_prop",
        "name.create_prop(" not in body,
    )
    check_true("generator still built", generator is not None)


# --- imports are returned for a class with nothing to import from ----------
# The `return` sat inside `if attributes or relationships`, so the 34 classes
# with neither -- Scope, Xform, Volume, most API schemas -- got None.
def test_imports_returned_for_bare_class() -> None:
    generator = geom_generator()
    for class_name in ("Scope", "Xform"):
        imports = generator._generate_imports(
            generator._determine_base_class(generator.classes_info[class_name]),
            generator.classes_info[class_name],
        )
        check_true(
            f"{class_name} imports are a string",
            isinstance(imports, str) and imports,
        )
        check_true(
            f"{class_name} imports SchemaKind",
            "SchemaKind" in imports,
        )


# --- regular attributes are emitted outside the namespace loop -------------
# The block was indented inside the namespaced-attribute loop, so a class only
# produced its plain attributes when it happened to have a namespaced one.
# Xformable has none, so it lost xformOpOrder and with it the xformOp API.
def test_regular_attributes_survive_without_namespaces() -> None:
    body = body_of(geom_generator(), "Xformable")
    check_true("Xformable keeps xformOpOrder", "xformOpOrder" in body)
    check_true("Xformable has no namespace group", "Attribute[namespace]" not in body)


# --- the nested XformOp declaration is emitted ------------------------------
# XformOp arrives through an #include, so the parser never sees it as an
# attribute; without this declaration regenerating xformable.py drops
# prim.xformOp.translate and the xformOpOrder upkeep that goes with it.
def test_nested_xformop_declaration() -> None:
    generator = geom_generator()
    body = body_of(generator, "Xformable")
    check_true(
        "Xformable declares the nested xformOp",
        "xformOp: XformOp = XformOp()" in body,
    )
    imports = generator._generate_imports(
        generator._determine_base_class(generator.classes_info["Xformable"]),
        generator.classes_info["Xformable"],
    )
    check_true("Xformable imports XformOp", "import XformOp" in imports)

    # The stub path has to emit it too. A stub shadows the module it sits beside, so a
    # member the .py declares and the .pyi omits is not untyped, it is invisible:
    # attribute access falls through to Prim.__getattr__, which is Any. That is how
    # xformOp ended up with no type while radius, extent and xformOpOrder all had one.
    stub = generator._generate_pyi_class_definition(
        "Xformable",
        generator._determine_base_class(generator.classes_info["Xformable"]),
        generator.classes_info["Xformable"],
        set(),
    )
    check_true("the stub declares xformOp too", "def xformOp(self) -> XformOp" in stub)
    # A bare annotation would make it a descriptor, because PropertySpec defines
    # __get__/__set__, and ty then checks the access against __get__'s first parameter --
    # a PrimSpec, not the Prim that Prim.__getattr__ hands out.
    check_true(
        "the stub declares it as a property, not a bare annotation",
        "xformOp: XformOp\n" not in stub,
    )
    stub_imports = generator._generate_pyi_imports(
        generator._determine_base_class(generator.classes_info["Xformable"]),
        generator.classes_info["Xformable"],
        [],
        set(),
    )
    check_true("the stub imports XformOp", "from .xformop import XformOp" in stub_imports)


# --- defaults are parsed ----------------------------------------------------
# tree-sitter-usd has no default_value node: `double radius = 1.0` parses as
# attribute_type / identifier / = / float, with the default as the sibling after
# `=`. The old branch looked for a node type that never occurs, so none of the
# 347 attributes had a default.
def test_attribute_defaults_are_parsed() -> None:
    generator = geom_generator()
    defaults = {}
    for class_name, info in generator.classes_info.items():
        for attribute in info["attributes"]:
            defaults[f"{class_name}.{attribute['name']}"] = attribute.get("default_value")

    check("Sphere.radius default", defaults.get("Sphere.radius"), 1.0)
    check_true(
        "some attributes carry defaults",
        any(value is not None for value in defaults.values()),
    )
    # A tuple default must not collapse to its first component.
    quat = defaults.get("PhysicsJoint.localRot0")
    if quat is not None:
        check_true("tuple default keeps every component", len(quat) == 4)


# --- a namespace head keeps a same-named plain member's type ----------------
# UsdGeomCamera declares a legacy top-level `float exposure` beside the
# `exposure:` namespace and pxr reports both. Typing the head as the namespace
# sentinel loses the plain member, and Camera then reports 21 of pxr's 22 names.
def test_namespace_head_keeps_plain_member_type() -> None:
    body = body_of(geom_generator(), "Camera")
    check_true(
        "exposure head is typed float",
        "exposure: AttributeSpec[float]" in body,
    )
    check_true("exposure children are still emitted", "exposure.iso" in body)


def main() -> int:
    for test in (
        test_leaf_attribute_is_assigned_not_created,
        test_imports_returned_for_bare_class,
        test_regular_attributes_survive_without_namespaces,
        test_nested_xformop_declaration,
        test_attribute_defaults_are_parsed,
        test_namespace_head_keeps_plain_member_type,
    ):
        try:
            test()
        except Exception as error:  # a crash is a failure too
            FAILURES.append(f"{test.__name__} raised {type(error).__name__}: {error}")

    for failure in FAILURES:
        print(f"FAIL {failure}")

    print(f"\n{len(FAILURES)} failure(s)" if FAILURES else "all generator checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
