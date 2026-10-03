"""End-to-end smoke test for the composed-stage API.

Covers the mechanisms the Prim/PrimSpec unification touches: shared layer
identity, typed views from both sides, schema fallback, LIVERPS strength,
variants, payload load state, relocates, relationships, metadata, and edit
layer isolation.

Run with:
    python workspace/test_prim_view.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pyusd import (
    Attribute,
    AttributeSpec,
    Layer,
    Prim,
    Property,
    Relationship,
    Stage,
)
from pyusd.geom import Camera, Mesh, Scope, Sphere, Xform
from pyusd.sdf import Specifier

FAILURES = []


def check(label, actual, expected):
    if actual != expected:
        FAILURES.append(f"{label}: got {actual!r}, expected {expected!r}")
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
    else:
        print(f"PASS {label}")


def check_true(label, value):
    check(label, bool(value), True)


# --- shared layer identity ------------------------------------------------
layer = Layer("smoke_identity.usda")
stage = Stage(layer)
check_true("shared impl", stage.root_layer._impl is layer._impl)
check_true(
    "layer.stage shares root impl", layer.stage.root_layer._impl is layer._impl
)

# --- typed views from both sides ------------------------------------------
xform = layer.def_(Xform, "/World")
check("layer.def_ returns Xform", type(xform).__name__, "Xform")
check_true("isinstance Xform", isinstance(xform, Xform))
check_true("isinstance Prim", isinstance(xform, Prim))
check("stage returns same class", type(stage["/World"]).__name__, "Xform")
check_true("stage view is a Prim", isinstance(stage["/World"], Prim))
check("layer[] is a Prim", isinstance(layer["/World"], Prim), True)
check_true("root_prim is a Prim", isinstance(layer.root_prim("World"), Prim))
check("views compare by path", stage["/World"] == stage["/World"], True)
check("view equals its path", stage["/World"] == "/World", True)
check("different stages differ", stage["/World"] == layer.stage["/World"], False)

# --- interned views --------------------------------------------------------
# Asking a stage for the same path twice is asking for the same thing, so the two
# views are the same object. Keyed by (path, class), which is also why a prim retyped
# by a stronger layer gets a new view instead of the one built for its old type.
# Interning is per Stage: stage and layer.stage are two Stage objects over one layer,
# so they keep separate caches and stay distinct, as the == check above already says.
check_true("same path is the same view", stage["/World"] is stage["/World"])
check_true("layer shares its stage's view", layer["/World"] is layer.stage["/World"])
check_true("def_ returns the interned view", xform is layer.stage["/World"])
check_true("a second stage is a distinct view", stage["/World"] is not layer.stage["/World"])
check("interning did not break ==", stage["/World"] == stage["/World"], True)

retyped = layer.def_(Mesh, "/Retyped")
check_true("explicit class agrees", Mesh(layer.stage, "/Retyped") is layer.stage["/Retyped"])
retyped_view = layer.stage["/Retyped"]
check("retyped starts as Mesh", type(retyped_view).__name__, "Mesh")
retyped.authored_prim.specifier = Specifier.Over
retyped.authored_prim._metadata._builtin_data["typeName"] = "Xform"
layer.stage.invalidate()
check("new type resolves", type(layer.stage["/Retyped"]).__name__, "Xform")
check_true("retyping makes a new view", layer.stage["/Retyped"] is not retyped_view)
check("old view keeps its class", type(retyped_view).__name__, "Mesh")

# --- schema fallback supplies the value type ------------------------------
xform.xformOp.translate = (4, 5, 6)
check("xformOp type", xform.xformOp.translate.type_name, "double3")
check("xformOpOrder maintained", list(xform.xformOpOrder.get()), ["xformOp:translate"])

mesh = layer.def_(Mesh, "/World/Mesh")
mesh.points = [(0, 0, 0), (1, 1, 1)]
check("points type from schema", mesh.points.type_name, "point3f[]")
check("points value", len(list(mesh.points.get())), 2)

# reading an unauthored declared property does not author it
check("unauthored prop not authored", mesh.subdivisionScheme.value_state, 0)
check_true(
    "unauthored prop still typed",
    mesh.subdivisionScheme.type_name.startswith("token"),
)

# --- edit layer isolation -------------------------------------------------
weak = Layer("smoke_weak.usda")
weak.def_(Xform, "/Shared")
weak["/Shared"].mass = 1.0

root = Layer("smoke_root.usda")
root.include(weak, prepend=False)
root_view = root.def_(Xform, "/Shared")
root_view.mass = 100.0

composed = Stage(root)
check("stronger layer wins", composed["/Shared"].mass.get(), 100.0)
check("source layer untouched", weak["/Shared"].mass.get(), 1.0)
check_true("edit target is the root layer", composed.edit_layer._impl is root._impl)
check("weak spec still authored", weak.prim_spec_at("/Shared").mass.get(), 1.0)

# --- references -----------------------------------------------------------
asset = Layer("smoke_asset.usda")
asset_spec = asset.prim_spec_at("/Asset") or asset.def_(Xform, "/Asset")
asset_spec.mass = 50.0
asset.default_prim = "Asset"

scene = Layer("smoke_scene.usda")
world = scene.def_(Xform, "/World")
world.reference(asset.prim_spec_at("/Asset"))

ref_stage = Stage(scene)
check("reference contributes value", ref_stage["/World"].mass.get(), 50.0)
check(
    "reference does not leak to source",
    asset.prim_spec_at("/Asset").mass.get(),
    50.0,
)

# --- payload load state is per stage --------------------------------------
payload_layer = Layer("smoke_payload.usda")
payload_spec = payload_layer.def_(Xform, "/Heavy")
payload_spec.heavy = "yes"

payload_scene = Layer("smoke_payload_scene.usda")
payload_world = payload_scene.def_(Xform, "/World")
payload_world.payload(payload_layer.prim_spec_at("/Heavy"))

stage_a = Stage(payload_scene)
stage_b = Stage(payload_scene)
check("payload visible before unload", stage_a["/World"].heavy.get(), "yes")
stage_a.unload("/World")
check("stage_a payload unloaded", stage_a["/World"].heavy.exists, False)
check("stage_b payload independent", stage_b["/World"].heavy.get(), "yes")
stage_a.load("/World")
check("stage_a payload reloaded", stage_a["/World"].heavy.get(), "yes")

# --- API schemas through the Prim view ------------------------------------
# Prim.__getattr__ routes *_api names to PrimSpec, which consults the API registry.
# It used to hand back a property handle for every non-underscore name, so these
# all resolved to a view over an attribute that does not exist.
api_stage = Stage()
api_prim = api_stage.def_(Mesh, "/M")

check("single-apply model_api", type(api_prim.model_api).__name__, "ModelAPI")
check("single-apply visibility_api", type(api_prim.visibility_api).__name__, "VisibilityAPI")
check("api object is the spec's", api_prim.model_api is api_prim.authored_prim.model_api, True)
check("non-api name is an Attribute", type(api_prim.xformOpOrder).__name__, "Attribute")

check("multiple-apply first", type(api_prim.collection_api("mine")).__name__, "CollectionAPI")
check("multiple-apply second", type(api_prim.collection_api("yours")).__name__, "CollectionAPI")
check("multiple-apply reuses instance", api_prim.collection_api("mine") is api_prim.collection_api("mine"), True)
check("multiple-apply distinct instances", api_prim.collection_api("mine") is not api_prim.collection_api("yours"), True)
api_schemas = list(api_prim.authored_prim.metadata.apiSchemas)
check("both collection instances registered",
      ["CollectionAPI:mine" in api_schemas, "CollectionAPI:yours" in api_schemas],
      [True, True])

# Applying a schema used to strip customData off the schema class itself, so the
# second application of the same multiple-apply schema raised KeyError.
from pyusd.collection_api import CollectionAPI

check("schema class meta survives application", "customData" in CollectionAPI.meta, True)

# apiSchemaCanOnlyApplyTo is checked against the prim's schema inheritance chain.
try:
    api_prim.material_x_config_api
    check("incompatible API refused", "no error", "ValueError")
except ValueError as error:
    check("incompatible API refused", "MaterialXConfigAPI" in str(error), True)

# --- variants -------------------------------------------------------------
# Variants are authored as real child prims, the way USDA encodes them inline.
# variant_set["name"] returns the storage spec, because a prim inside a variant
# has no absolute stage path and so cannot be a (stage, path) view.
var_layer = Layer("smoke_variants.usda")
model = var_layer.def_(Xform, "/Model")
high = model.authored_prim.def_(Xform, "high")
high.level = 2
low = model.authored_prim.def_(Xform, "low")
low.level = 1
model.variant_sets.select_variant("lod", "high")

var_stage = Stage(var_layer)
check("selected variant name", model.variant_sets.get_variant_selection("lod"), "high")
check("variant set is iterable", "lod" in model.variant_sets, True)
check("variant child reachable", var_stage.has_prim("/Model/high"), True)
check("variant contributes value", var_stage["/Model/high"].level.get(), 2)

model.variant_sets.select_variant("lod", "low")
var_stage.invalidate()
check("variant switch resolves", var_stage["/Model/low"].level.get(), 1)

# --- relocates ------------------------------------------------------------
rel_layer = Layer("smoke_relocate.usda")
old = rel_layer.def_(Xform, "/Old")
old.moved = 1
rel_layer.relocate("/Old", "/New")

rel_stage = Stage(rel_layer)
check("relocate hides source", rel_stage.has_prim("/Old"), False)
check("relocate exposes target", rel_stage.has_prim("/New"), True)
check("relocated value readable", rel_stage["/New"].moved.get(), 1)

# --- namespace population -------------------------------------------------
pop_layer = Layer("smoke_population.usda")
pop_layer.def_(Xform, "/Visible")
pop_layer.class_("/ClassOnly")
pop_layer.over_("/OverOnly")

pop_stage = Stage(pop_layer)
check("def populates namespace", pop_stage.has_prim("/Visible"), True)
# over and class supply opinions but never create namespace children; they stay
# reachable by explicit path, which is what pxr's GetPrimAtPath reports too.
check("children exclude class/over", sorted(pop_stage.child_names()), ["Visible"])
check("class reachable by explicit path", pop_stage.has_prim("/ClassOnly"), True)
check("over reachable by explicit path", pop_stage.has_prim("/OverOnly"), True)
check(
    "untyped prim is a bare Prim",
    type(pop_stage["/ClassOnly"]).__name__,
    "Prim",
)

# --- relationships --------------------------------------------------------
rel2_layer = Layer("smoke_rel2.usda")
rel2_layer.def_(Scope, "/Target")
rel2_src = rel2_layer.def_(Scope, "/Src")
rel2_src.link.rel(rel2_layer.prim_spec_at("/Target"))
check("relationship target resolves", len(rel2_src.link.targets), 1)

# --- resolved handles are Attribute or Relationship, never the stored spec ---
split_layer = Layer("smoke_handles.usda")
split = Stage(split_layer)
split_sphere = split.def_(Sphere, "/S")
split_camera = split.def_(Camera, "/C")

check("prim attribute handle type", type(split_sphere.radius).__name__, "Attribute")
check_true("prim attribute is an Attribute", isinstance(split_sphere.radius, Attribute))
check_true(
    "stored spec is not a handle",
    not isinstance(split_sphere.radius.resolved_property, Attribute),
)
check_true(
    "stored spec is an AttributeSpec",
    isinstance(split_sphere.radius.resolved_property, AttributeSpec),
)
check_true("handle is a Property", isinstance(split_sphere.radius, Property))

# pxr hands back an invalid-but-authorable attribute for a name nothing declares,
# so prim.doesNotExist exists as an Attribute with exists False.
check("unknown name exists False", split_sphere.doesNotExist.exists, False)
check("unknown name is_valid False", split_sphere.doesNotExist.is_valid(), False)
check("unknown name is an Attribute", type(split_sphere.doesNotExist).__name__, "Attribute")
split_sphere.doesNotExist = 3
check("unknown name authors", split_sphere.doesNotExist.get(), 3)
check("unknown name now exists", split_sphere.doesNotExist.exists, True)

split_rel = split._create_relationship("/S", "link")
check("relationship handle type", type(split_rel).__name__, "Relationship")
check_true("prim attribute is not a Relationship", not isinstance(split_sphere.radius, Relationship))
check_true("relationship is a Property", isinstance(split_rel, Property))
check("prim resolves rel to Relationship", type(split_sphere.link).__name__, "Relationship")

# A nested schema owns its members, so xformOp.translate stays reachable; a plain
# attribute has none, so a miss is an error rather than a property called
# radius:foo that nothing declared.
check_true("xformOp child is an Attribute", isinstance(split_sphere.xformOp.translate, Attribute))
split_sphere.xformOp.translate = (1, 2, 3)
check("xformOp authoring updates xformOpOrder", split_sphere.xformOpOrder.get(), ["xformOp:translate"])
try:
    split_sphere.radius.nonexistent
    check("plain attribute member miss raises", False, True)
except AttributeError:
    check("plain attribute member miss raises", True, True)

# A declared namespace child is reachable even before a layer materialises it,
# which is what makes prim.exposure.iso authorable on a fresh Camera.
check("declared ns child is an Attribute", type(split_camera.exposure.iso).__name__, "Attribute")
split_camera.exposure.iso = 1.0
check("declared ns child authors", split_camera.exposure.iso.get(), 1.0)
try:
    split_sphere.exposure.iso
    check("undeclared ns child raises", False, True)
except AttributeError:
    check("undeclared ns child raises", True, True)

# --- schema type survives a round trip ------------------------------------
rt_layer = Layer("smoke_roundtrip.usda")
rt_layer.def_(Xform, "/A")
rt_mesh = rt_layer.def_(Mesh, "/B")
rt_text = rt_layer.to_str()
check_true("Mesh type in text", "def Mesh \"B\"" in rt_text)

# --- default prim ---------------------------------------------------------
dp_layer = Layer("smoke_default.usda")
dp_layer.def_(Xform, "/D")
dp_layer.default_prim = "D"
check("default prim name", dp_layer._default_prim_name, "D")
check("default prim view", type(dp_layer.default_prim).__name__, "Xform")

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s):")
    for failure in FAILURES:
        print(f"  {failure}")
    raise SystemExit(1)

print("all smoke checks passed")
