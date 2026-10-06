"""End-to-end smoke test for the composed-stage API.

Covers the mechanisms the Prim/PrimSpec unification touches: shared layer
identity, typed views from both sides, schema fallback, LIVERPS strength,
variants, payload load state, relocates, relationships, metadata, and edit
layer isolation.

Run with:
    python workspace/test_prim_view.py
"""

import sys
import tempfile
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
from pyusd.model_api import ModelAPI
from pyusd.prim_spec import PrimSpec
from pyusd.sdf import Specifier

ROOT = Path(__file__).resolve().parent.parent

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

# Arc targets accept the view, not just the stored spec. A Prim used to be appended to
# the arc list as-is and serialised as "prepend references = Prim(</t>)", which is not a
# reference and does not survive a round trip through OpenUSD. Passing one is the
# natural thing to do, so it is reduced to its spec instead.
arc_asset = Layer("smoke_arc_asset.usda")
arc_asset.def_(Xform, "/Source")
arc_stage = Stage(arc_asset)
arc_src = arc_stage["/Source"]
arc_dst = arc_stage.def_(Xform, "/Dest")
arc_dst.reference(arc_src)
check("reference accepts a Prim", len(arc_dst.authored_prim._references), 1)
check_true(
    "the stored arc is a spec, not a view",
    isinstance(arc_dst.authored_prim._references[0], PrimSpec),
)
check_true(
    "the serialised arc is a path, not a repr",
    "Prim(" not in arc_stage.root_layer.to_str(),
)
# All four arc kinds go through the same reduction.
for kind in ("inherit", "payload", "specialize"):
    getattr(arc_dst, kind)(arc_src)
arcs = arc_dst.authored_prim
check("inherit accepted a Prim", len(arcs._inherits), 1)
check("payload accepted a Prim", len(arcs._payloads), 1)
check("specialize accepted a Prim", len(arcs._specializes), 1)
arc_dst.remove_reference(arc_src)
check("remove_reference accepts a Prim", len(arc_dst.authored_prim._references), 0)

# A string target is USDA arc syntax, and it is what round trips: the serializer writes
# strings verbatim and OpenUSD reads them back. These spellings were each checked against
# pxr 0.26.8 with Sdf.Layer.ImportFromString, which parses without resolving.
str_stage = Stage(Layer("smoke_str_arcs.usda"))
str_prim = str_stage.def_(Xform, "/S")
str_prim.reference("/t")
str_prim.payload("@./a.usda@</A>")
str_prim.specialize("</c>")
str_prim.inherit("</Base>")
check(
    "bare path gains its brackets",
    str(list(str_prim.authored_prim._references)),
    "['</t>']",
)
check(
    "asset arc is stored verbatim",
    list(str_prim.authored_prim._payloads),
    ["@./a.usda@</A>"],
)
str_text = str_stage.root_layer.to_str()
check_true("payload is spelled the way USD spells it", "prepend payload = " in str_text)
check_true("the plural spelling is gone", "prepend payloads" not in str_text)

# Both spellings still read, so a file written before that fix is not lost.

for spelling in ("payload", "payloads"):
    with tempfile.NamedTemporaryFile(
        "w", suffix=".usda", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(
            '#usda 1.0\n\ndef Xform "P" (\n    prepend ' + spelling
            + ' = @./a.usda@</A>\n)\n{\n    double x = 1\n}\n'
        )
        rt_path = handle.name
    check(
        f"{spelling} reads back",
        list(Layer.load(rt_path).prim_spec_at("/P")._payloads),
        ["@./a.usda@</A>"],
    )

# Each accepted form has to compose, not just serialise: the reader takes an asset
# reference from the leading @, and a prim path from the brackets.
arc_dir = Path(tempfile.mkdtemp())
arc_asset = arc_dir / "arc_asset.usda"
arc_asset.write_text('#usda 1.0\n\ndef Xform "A"\n{\n    double mass = 7\n}\n')
default_asset = Layer(str(arc_dir / "arc_default.usda"))
default_asset.def_(Xform, "Default").mass = 9
default_asset.default_prim = "Default"
default_asset.save()

for label, target, expected in (
    ("internal bare path", "/T", 3),
    ("internal bracketed", "</T>", 4),
    ("asset with prim path", f"@{arc_asset}@</A>", 7),
    ("asset without prim path", f"@{arc_dir / 'arc_default.usda'}@", 9),
):
    compose_stage = Stage(Layer())
    source = compose_stage.def_(Xform, "/T")
    source.mass = 3 if "bare" in label else 4
    dest = compose_stage.def_(Xform, "/P")
    dest.reference(target)
    check(f"{label} composes", dest.mass.get(), expected)

# Anything the engine cannot resolve is refused. A string with no leading @ has no asset
# and no brackets means no prim path, so it composes to nothing while looking stored --
# and USD does not parse it either.
for bad in ("./a.usda", "a.usda", "rel/path", "", "<>"):
    try:
        str_prim.reference(bad)
        check(f"{bad!r} is refused", False, True)
    except ValueError:
        check(f"{bad!r} is refused", True, True)

# Two things OpenUSD rejects, refused here rather than written into a file that will not
# open: an asset arc for inherits, which is internal-only, and an asset path with the
# leading @ left off.
try:
    str_prim.inherit("@./a.usda@</A>")
    check("inherits refuses an asset arc", False, True)
except ValueError:
    check("inherits refuses an asset arc", True, True)
try:
    str_prim.reference("./a.usda@</A>")
    check("a missing leading @ is refused", False, True)
except ValueError:
    check("a missing leading @ is refused", True, True)

# A prim that exists only as a composed result has no stored form to point at, so it
# is refused rather than silently written as something unreadable.
try:
    arc_dst.inherit(Stage(Layer("smoke_arc_unauthored.usda"))["/Nowhere"])
    check("an unauthored target is refused", False, True)
except KeyError:
    check("an unauthored target is refused", True, True)

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

# --- defaultPrim is readable and assignable ---------------------------------
# The read side always existed and the write side did not, so stage.default_prim = prim
# raised and the only way in was stage.metadata.defaultPrim. That is an asymmetry, not a
# decision, and it is the one thing the referencing example could not do.
dp_layer = Layer("smoke_defaultprim.usda")
dp_stage = Stage(dp_layer)
dp_hello = dp_stage.def_(Xform, "/hello")
dp_hello.def_(Xform, "/child")

check("default prim starts unset", dp_stage.default_prim, None)
dp_stage.default_prim = dp_hello
check("assigning a prim sets it", dp_stage.default_prim.path, "/hello")
check("assigned default prim is the same view", dp_stage.default_prim is dp_hello, True)
check_true(
    "authored into the edit layer",
    dp_layer.metadata._builtin_data.get("defaultPrim") == "/hello",
)

# A bare name is shorthand for a path from the stage root, which is what the getter
# already assumed; it is not relative to the default prim being replaced.
dp_stage.default_prim = "child"
check("a bare name means a root path", dp_stage.default_prim.path, "/child")

try:
    dp_stage.default_prim = Stage(Layer()).def_(Xform, "/elsewhere")
    check("a foreign prim is refused", False, True)
except ValueError:
    check("a foreign prim is refused", True, True)

try:
    dp_stage.default_prim = 5
    check("a non-path is refused", False, True)
except TypeError:
    check("a non-path is refused", True, True)

check_true("defaultPrim reaches the serialized text", 'defaultPrim = "/child"' in dp_layer.to_str())

# --- new=True means new, even when the file is there --------------------------
# LayerCache.materialize loads a layer lazily when it is empty and the file exists,
# which is why Layer("out.usda") appears to read the file even though Layer.__init__
# never parses anything. A caller that says new=True must survive that path too, so
# the check below queries the stage rather than trusting the constructor.
new_dir = Path(tempfile.mkdtemp())
new_file = new_dir / "new_flag.usda"
new_file.write_text('#usda 1.0\n\ndef Xform "hello"\n{\n    def Sphere "world"\n    {\n    }\n}\n')

check_true("file on disk exists", new_file.exists())
loaded = Stage(str(new_file))
check_true(
    "default loads the file",
    "/hello" in [p.path for p in loaded.traverse()],
)

fresh = Stage(str(new_file), new=True)
check_true("new=True layer carries the flag", fresh.root_layer._is_new)
check(
    "new=True stage is empty",
    [p.path for p in fresh.traverse() if p.path != "/"],
    [],
)
check("new=True stage_has_prim is falsy", bool(fresh.stage_has_prim("/hello")), False)
check_true("new=True stage never parsed the file", not fresh.root_layer._loaded)

# The flag lives on the layer, so going through Layer first has to hold too, and the
# lazy materialize path is where that is actually decided.
fresh_layer = Layer(str(new_file), new=True)
check("new=True Layer is empty before querying", list(fresh_layer._root_prims), [])
check(
    "new=True Layer stays empty after querying",
    [p.path for p in fresh_layer.stage.traverse() if p.path != "/"],
    [],
)
check("new=True Layer never parsed the file", fresh_layer._loaded, False)

# A new layer must not take the registry slot the real one uses, in either order.
check_true(
    "new=True does not clobber the loaded layer",
    "/hello" in [p.path for p in Stage(str(new_file)).traverse()],
)
check(
    "loaded layer still sees its content after a new one",
    [p.path for p in loaded.traverse()],
    [p.path for p in Stage(str(new_file)).traverse()],
)

# Two new layers for one path are independent, the same way two anonymous layers are:
# an empty scratch layer that carries a name is not that file's layer.
a_new = Stage(str(new_file), new=True)
b_new = Stage(str(new_file), new=True)
a_new.def_(Xform, "/OnlyInA")
check("new=True stages are independent", [p.path for p in b_new.traverse()], [])
check("authoring into a new stage works", [p.path for p in a_new.traverse()], ["/OnlyInA"])

# And the point of the flag: authoring over a file that exists leaves only what was
# authored.
overwrite = Stage(str(new_file), new=True)
overwrite.def_(Xform, "/onlyThis")
overwrite.root_layer.save()
# Read the file rather than going through Layer.load: within one process the registry
# still holds the layer that Stage(str(new_file)) made earlier, and Layer.load hands
# that back instead of re-reading -- which is the "one load per path" rule, not a
# failure to overwrite.
check_true("overwrite wrote the file", new_file.exists())
check_true("overwrote file lost the old prim", "hello" not in new_file.read_text())
check_true("overwrote file has the new prim", "onlyThis" in new_file.read_text())
new_file.unlink()
new_dir.rmdir()

# --- api accessors are declarations, not implementations ---------------------
# Prim.__getattr__ routes every *_api name to PrimSpec.__getattr__, which consults the
# registry, checks apiSchemaCanOnlyApplyTo and hands back the schema object or an
# APIWrapper. A generated body per accessor would be a second implementation of a path
# that already exists -- 41 of them, three lines each. They are declarations under
# if TYPE_CHECKING instead, so the class carries them for a type checker and the runtime
# never sees them.
check_true("API accessor works at runtime", isinstance(api_prim.model_api, ModelAPI))
# If the class really had these attributes, __getattr__ would never run and the API
# registry, apiSchemaCanOnlyApplyTo and the multiple-apply wrapper would all be bypassed.
check_true(
    "API accessors are not real class attributes",
    not any(
        name in vars(klass)
        for klass in type(api_prim).__mro__
        for name in ("model_api", "collection_api")
    ),
)
check(
    "multiple-apply accessor still routes",
    type(api_prim.collection_api("via_getattr")).__name__,
    "CollectionAPI",
)
# Assigning over an *_api name still authors a property of that name, which is
# pre-existing Prim.__setattr__ behaviour; the point is that removing the generated
# bodies did not change it.
api_prim.model_api = "a property, not a schema"
check("assignment authors a property of that name", api_prim.has_prop("model_api"), True)

# --- a working-directory relative arc survives being written to a file ---------
# A relative asset path is read relative to the layer holding it. A layer with no file
# name has no directory, so the working directory stands in -- and the same string means a
# different file the moment that layer is written somewhere. These are the paths that get
# re-expressed against the destination; nothing else is touched, which is what keeps a
# relative path that came out of a file byte for byte identical.
import os

arc_root = tempfile.mkdtemp()
arc_pkg = Path(arc_root) / "pkg"
arc_pkg.mkdir()
asset_body = '#usda 1.0\n\ndef Xform "A"\n{\n    double mass = 7\n}\n'
(Path(arc_root) / "asset.usda").write_text(asset_body)
(Path(arc_pkg) / "local.usda").write_text(asset_body)

previous_cwd = os.getcwd()
os.chdir(arc_root)
try:
    anonymous = Stage(Layer())
    referenced = anonymous.def_(Xform, "/P")
    referenced.reference("@./asset.usda@</A>")
    check("cwd relative arc resolves while authoring", referenced.mass.get(), 7.0)
    check(
        "and is marked as working-directory relative",
        anonymous.root_layer._impl._cwd_relative_assets,
        {"./asset.usda"},
    )

    anonymous.root_layer.save(str(arc_pkg / "scene.usda"))
    written = (arc_pkg / "scene.usda").read_text()
    check_true("written relative to the layer", "@../asset.usda@</A>" in written)

    # The whole point: the file opens from anywhere.
    elsewhere = tempfile.mkdtemp()
    os.chdir(elsewhere)
    check(
        "reopened from an unrelated directory",
        Stage(str(arc_pkg / "scene.usda"))["/P"].mass.get(),
        7.0,
    )

    os.chdir(arc_root)
    anchored_layer = Layer(str(arc_pkg / "anchored.usda"), new=True)
    anchored = Stage(anchored_layer).def_(Xform, "/Q")
    anchored.reference("@./local.usda@</L>")
    # The reported case: the layer has a file name and the author still wrote a path that
    # reads as working-directory relative. to_str alone is enough to fix it -- no save.
    named = Layer(str(arc_pkg / "named.usda"), new=True)
    named_prim = Stage(named).def_(Xform, "/Named")
    named_prim.reference("@./asset.usda@</A>")
    check_true(
        "a named layer rewrites a cwd-relative path in to_str",
        "@../asset.usda@</A>" in named.to_str(),
    )
    check_true(
        "and never turns an arc into a repr",
        "Prim(" not in named.to_str(),
    )

    # Every relative asset path authored through the API is recorded, whether or not the
    # layer has a file name -- here it does, and the author still wrote a path that reads
    # as working-directory relative. What decides whether to rebase is whether the
    # as-stored reading already resolves, so a path that was already correct is left alone.
    check(
        "a relative path is recorded even with a file name",
        anchored_layer._impl._cwd_relative_assets,
        {"./local.usda"},
    )
    anchored_layer.save()
    check_true(
        "but a path already correct for the layer is written unchanged",
        "@./local.usda@</L>" in (arc_pkg / "anchored.usda").read_text(),
    )
finally:
    os.chdir(previous_cwd)

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

# --- restored operators -----------------------------------------------------
# A composed handle is not a Data subclass, so the arithmetic Data used to supply
# has to be restated on Attribute. The in-place forms have to author, and the
# assignment an augmented statement finishes with has to be understood as "that
# value", not "that handle".
ops_layer = Layer("smoke_ops.usda")
ops = Stage(ops_layer)
ops_a = ops.def_(Sphere, "/A")
ops_b = ops.def_(Sphere, "/B")
ops_a.radius = 5.0
ops_b.radius = 1.0

check("handle + scalar", ops_a.radius + 1, 6.0)
check("scalar + handle", 1 + ops_a.radius, 6.0)
check("handle - scalar", ops_a.radius - 1, 4.0)
check("handle * scalar", ops_a.radius * 2, 10.0)
check("handle / scalar", ops_a.radius / 2, 2.5)
check("handle ** scalar", ops_a.radius**2, 25.0)
check("handle % scalar", ops_a.radius % 3, 2.0)
check("handle // scalar", ops_a.radius // 2, 2.0)
check("handle > scalar", ops_a.radius > 3, True)
check("scalar < handle", ops_a.radius > 3, True)
check("handle <= scalar", ops_a.radius <= 5.0, True)
check("handle + handle", ops_a.radius + ops_b.radius, 6.0)
check("handle + stored spec", ops_a.radius + ops_b.radius.resolved_property, 6.0)

ops_a.radius += 1
check("+= authors", ops_a.radius.get(), 6.0)
ops_a.radius *= 2
check("*= authors", ops_a.radius.get(), 12.0)
ops_a.radius -= 3
check("-= authors", ops_a.radius.get(), 9.0)
ops_a.radius /= 2
check("/= authors", ops_a.radius.get(), 4.5)
ops_a.radius **= 2
check("**= authors", ops_a.radius.get(), 20.25)
ops_a.radius //= 3
check("//= authors", ops_a.radius.get(), 6.0)
ops_a.radius %= 3
check("%= authors", ops_a.radius.get(), 0.0)

# An augmented statement also assigns its result back, so the handle the operator
# returned has to unwrap on the way in rather than be authored as a value.
ops_a.radius = ops_b.radius
check("assigning a handle authors its value", ops_a.radius.get(), 1.0)

ops_x = ops.def_(Xform, "/X")
ops_x.xformOp.translate = (1.0, 2.0, 3.0)
check("len of a vector attribute", len(ops_x.xformOp.translate), 3)
check("indexing a vector attribute", ops_x.xformOp.translate[0], 1.0)
check_true("in rejects a non-member", 9.0 not in ops_x.xformOp.translate)

# The handle and the stored spec must come from one implementation. They were once
# two copies of the same thirty methods, agreeing only because they were written to
# agree, and the reason they cannot be one base class is that Data owns a stored
# value while a handle composes one -- the arithmetic is what they actually share.
check(
    "handle and spec share one arithmetic",
    Attribute.__add__ is AttributeSpec.__add__,
    True,
)
check("spec arithmetic comes from the same mixin", Attribute.__lt__ is AttributeSpec.__lt__, True)

stored = AttributeSpec(float, name="stored", value=5.0)
stored += 1
check("stored spec += still rewrites itself", stored.get(), 6.0)
check("stored spec * scalar", stored * 2, 12.0)
check("stored spec ordering", stored > 1, True)
check("stored spec reflected", 10 - stored, 4.0)

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
