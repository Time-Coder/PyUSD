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
from pyusd.composition import CompositionEngine, normalize_arc_text
from pyusd.geom import Camera, Mesh, Scope, Sphere, Xform
from pyusd.model_api import ModelAPI
from pyusd.prim_spec import PrimSpec
from pyusd.property_spec import PropertySpec
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
check_true("shared layer identity", stage.root_layer is layer)
check_true(
    "layer.stage shares root layer", layer.stage.root_layer is layer
)

# --- interned layers -------------------------------------------------------
# Constructing the same file twice hands back the same layer object, which is what
# makes the `is self` guards in add_root_prim / remove_root_prim mean what they say:
# a spec remembers the one layer object that owns it. Before interning, a second
# construction produced an equal-but-distinct wrapper and remove_root_prim through
# it refused the spec.
layer_again = Layer("smoke_identity.usda")
check_true("same file is the same layer", layer_again is layer)
check_true("a different file is not", Layer("smoke_other.usda") is not layer)
layer.def_(Xform, "/Owned")
owned_spec = layer.prim_spec_at("/Owned")
layer_again.remove_root_prim(owned_spec)
check_true("remove through the second name works", owned_spec.layer is None)
layer.add_root_prim(owned_spec)
revision_before = layer.revision
layer.add_root_prim(owned_spec)
check("re-adding a root prim is a no-op", layer.revision, revision_before)
new_named_1 = Layer("smoke_new_flag.usda", new=True)
new_named_2 = Layer("smoke_new_flag.usda", new=True)
check_true("new=True layers stay independent", new_named_1 is not new_named_2)
check_true("and do not intern with the opened one", new_named_1 is not layer)
check_true("anonymous layers stay independent", Layer() is not Layer())


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

# --- parent is a path relationship -----------------------------------------
# pxr's GetParent. Derived from the path, not looked up: a parent composes
# whenever its child does, so there is nothing for the engine to answer. None at
# the root is pxr's answer, not a missing-key error.
check("parent path", layer.stage["/Retyped"].parent_path, "/")
check_true(
    "parent is the composed view",
    layer.stage["/Retyped"].parent is layer.stage["/"],
)
check_true("root has no parent path", stage["/"].parent_path is None)
check_true("root has no parent", stage["/"].parent is None)
check_true(
    "parent is the interned view",
    layer.stage["/Retyped"].parent is layer.stage["/"],
)
# A parent whose own typeName comes only from a weak layer is still the parent.
weak_only = Layer("smoke_parent_weak.usda")
weak_only.def_(Xform, "/W")
weak_only_root = Layer("smoke_parent_root.usda")
weak_only_root.include(weak_only)
weak_only_root.def_(Xform, "/W/Child")
parent_stage = Stage(weak_only_root)
check_true(
    "a weak-layer parent is still a parent",
    parent_stage["/W/Child"].parent is parent_stage["/W"],
)
check("and keeps its own composed type", type(parent_stage["/W/Child"].parent).__name__, "Xform")

# --- the answering form of has_prim ----------------------------------------
# GetPrimAtPath. __getitem__ cannot be it: a missing prim raises KeyError there,
# and a lookup that guesses is worse than one that says no.
check_true("prim at path answers", stage.get_prim_at_path("/World") is stage["/World"])
check("root path answers", stage.get_prim_at_path("/"), stage["/"])
check_true("missing path answers None", stage.get_prim_at_path("/Nope") is None)
check_true("layer delegates to it", layer.prim_at("/World") is layer.stage["/World"])
check("layer answers None too", layer.prim_at("/Nope"), None)

# --- schema fallback supplies the value type ------------------------------
xform.xformOp.translate = (4, 5, 6)
check("xformOp type", xform.xformOp.translate.type_name, "double3")
check("xformOpOrder maintained", list(xform.xformOpOrder.get()), ["xformOp:translate"])

mesh = layer.def_(Mesh, "/World/Mesh")
check("nested parent path", mesh.parent_path, "/World")
check_true("nested parent is the view", mesh.parent is layer.stage["/World"])
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
check_true("edit target is the root layer", composed.edit_layer is root)
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

# A bare asset path is completed to "@asset@" rather than refused, because that is what pxr
# does with the same string: Sdf.Reference("a.usda") takes it as-is, and ExportToString
# writes it back as "@a.usda@". Its parser is the strict side -- in a references list "a.usda"
# and "a.usda</A>" are both rejected -- so the wrapping is what makes the string mean anything.
bare_stage = Stage(Layer(str(Path(tempfile.mkdtemp()) / "bare.usda"), new=True))
bare_prim = bare_stage.def_(Xform, "/Bare")
for bare in ("a.usda", "./a.usda", "rel/path.usda"):
    bare_prim.reference(bare)
    check(
        f"a bare {bare!r} is wrapped",
        list(bare_prim.authored_prim._references)[0],
        "@" + bare + "@",
    )

# A path that only lost its opening @ keeps the closing one it still has; wrapping the whole
# string again would produce "@a.usda@</A>@" rather than "@a.usda@</A>".
half_stage = Stage(Layer(str(Path(tempfile.mkdtemp()) / "half.usda"), new=True))
half_prim = half_stage.def_(Xform, "/Half")
half_prim.reference("./a.usda@</A>")
check(
    "a missing opening @ is supplied, not wrapped twice",
    list(half_prim.authored_prim._references)[0],
    "@./a.usda@</A>",
)

# The <...> in a bare asset path is a target prim, not an internal reference. Left alone,
# "a.usda</A>" would resolve as an internal arc to "/A" of this same layer, so the @ has to
# go in before the brackets are read as a prim path.
check(
    "a bare path with a target prim is not read as an internal arc",
    normalize_arc_text("a.usda</A>"),
    "@a.usda@</A>",
)

# What is left over has no arc in it at all, and is refused rather than stored as something
# that composes to nothing while looking stored.
for bad in ("", "<>"):
    try:
        str_prim.reference(bad)
        check(f"{bad!r} is refused", False, True)
    except ValueError:
        check(f"{bad!r} is refused", True, True)

# Class inheritance is internal-only, and OpenUSD rejects an asset arc for it outright, so
# that one is refused rather than written into a file that will not open.
try:
    str_prim.inherit("@./a.usda@</A>")
    check("inherits refuses an asset arc", False, True)
except ValueError:
    check("inherits refuses an asset arc", True, True)

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
    dp_layer.metadata._builtin_data.get("defaultPrim") == "hello",
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

check_true("defaultPrim reaches the serialized text", 'defaultPrim = "child"' in dp_layer.to_str())

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
check("new=True get_prim_at_path is None", fresh.get_prim_at_path("/hello"), None)
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
    # The mark records where the spelling was made relative to as well as what it names,
    # because those are the two things a later re-expression needs. An anonymous layer has no
    # directory of its own, so the working directory is what it was made relative to.
    marked = anonymous.root_layer._cwd_relative_assets
    check(
        "and is marked as working-directory relative",
        list(marked),
        ["./asset.usda"],
    )
    check(
        "recording the file it was written against",
        marked["./asset.usda"],
        (str(Path(arc_root) / "asset.usda"), arc_root),
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
    # Case must survive: normcase lowercases on Windows, and feeding that to relpath
    # turned "@./Asset.usda@" into "@../asset.usda@", naming a file that does not exist
    # on a case-sensitive filesystem.
    cased = Layer(str(arc_pkg / "cased.usda"), new=True)
    cased_prim = Stage(cased).def_(Xform, "/Cased")
    cased_prim.reference("@./asset.usda@</A>")
    cased_arc = next(
        line for line in cased.to_str().splitlines() if "references" in line
    )
    check_true("case is preserved when rebasing", "asset.usda@" in cased_arc)


    nested = Path(tempfile.mkdtemp()) / "inner"
    nested.mkdir()
    (nested / "Same.usda").write_text(asset_body)
    previous = os.getcwd()
    os.chdir(nested)
    try:
        beside = Layer(str(arc_pkg / "beside.usda"), new=True)
        beside_prim = Stage(beside).def_(Xform, "/Beside")
        beside_prim.reference("@./Same.usda@</A>")
        beside_arc = next(
            line for line in beside.to_str().splitlines() if "references" in line
        )
        check_true("a rebased path keeps its case", "Same.usda@" in beside_arc)
    finally:
        os.chdir(previous)

    # A named layer corrects the spelling as it is authored, not on the way out. Correcting
    # it only at serialization left the layer pointing at one file before save() and another
    # after, silently -- to_str said "../Asset.usda@" while composition still resolved
    # "./Asset.usda@" against the layer's own directory and found nothing.
    live = Layer(str(arc_pkg / "live.usda"), new=True)
    live_prim = Stage(live).def_(Xform, "/Live")
    live_prim.reference("@./asset.usda@</A>")
    check("a named layer composes before it is saved", Stage(live)["/Live"].mass.get(), 7.0)
    check_true(
        "and stores the spelling the layer will read",
        "@../asset.usda@</A>" in live.to_str(),
    )

    # Saving elsewhere must not change which file is meant: the path was written against the
    # working directory, and the recorded target is what says so, not the directory it
    # happened to be authored in.
    moved_to = Path(tempfile.mkdtemp()) / "moved_to"
    moved_to.mkdir()
    (moved_to / "asset.usda").write_text(asset_body.replace("7", "99"))
    # The layer sits in a subdirectory, so its own reading of the path and the working
    # directory's disagree -- which is the only case where anything is recorded at all.
    moved = Layer(str(Path(arc_root) / "pkg" / "moved.usda"), new=True)
    Stage(moved).def_(Xform, "/Moved").reference("@./asset.usda@</A>")
    moved.save(str(moved_to / "moved.usda"))
    check(
        "saving elsewhere keeps the file the author meant",
        Stage(str(moved_to / "moved.usda"))["/Moved"].mass.get(),
        7.0,
    )

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

    # A path that already means the right file is not recorded at all. There is a directory
    # to correct against, the as-stored reading resolves, and so there is nothing to fix --
    # and nothing recorded that a later move could mis-apply. The layer keeps the author's
    # exact spelling.
    check(
        "a path already correct for a named layer is not recorded",
        anchored_layer._cwd_relative_assets,
        {},
    )
    anchored_layer.save()
    check_true(
        "but a path already correct for the layer is written unchanged",
        "@./local.usda@</L>" in (arc_pkg / "anchored.usda").read_text(),
    )
    # Spelling is preserved too, "./" included: a path that needs no rewrite is returned
    # untouched, and a rewrite can never produce a bare filename, because that would mean
    # the target sits beside the layer -- the case that is not rewritten at all.
    check_true(
        "an untouched path keeps its ./ prefix",
        "references = @./local.usda@</L>" in (arc_pkg / "anchored.usda").read_text(),
    )

    # And a rewritten one keeps it too. An authored path can leave the layer's directory
    # and come back -- "../../Pkg/Asset.usda@" written from two levels down rebases to the
    # bare "Asset.usda" -- so the prefix has to be put back rather than assumed away.
    detour = Path(tempfile.mkdtemp()) / "Pkg"
    (detour / "deep" / "deeper").mkdir(parents=True)
    (detour / "Asset.usda").write_text(asset_body)  # two levels up from the cwd
    previous = os.getcwd()
    os.chdir(detour / "deep" / "deeper")
    try:
        round_trip = Layer(str(detour / "detour.usda"), new=True)
        Stage(round_trip).def_(Xform, "/Detour").reference("@../../Asset.usda@</A>")
        detour_arc = next(
            line for line in round_trip.to_str().splitlines() if "references" in line
        )
        check_true(
            "a rewritten path keeps the ./ prefix USD writes",
            "@./Asset.usda@</A>" in detour_arc,
        )
    finally:
        os.chdir(previous)
finally:
    os.chdir(previous_cwd)

# --- variants -------------------------------------------------------------
# A variant's content lives on the variant spec rather than on the prim: a prim
# inside a variant has no absolute stage path, so it cannot be a (stage, path)
# view. variant_sets[name][variant] is what content is authored through, and
# variant_sets[name].select_variant(...) only records which variant is chosen.
var_layer = Layer("smoke_variants.usda")
model = var_layer.def_(Xform, "/Model")
var_lod = model.authored_prim.variant_sets["lod"]
var_lod["high"].def_(Xform, "high_child").level = 2
var_lod["low"].def_(Xform, "low_child").level = 1
model.variant_sets["lod"].select_variant("high")

var_stage = Stage(var_layer)
check("selected variant name", model.variant_sets["lod"].selection, "high")
check("variant set is iterable", "lod" in model.variant_sets, True)
check("selected variant content composes", var_stage.has_prim("/Model/high_child"), True)
check("variant contributes value", var_stage["/Model/high_child"].level.get(), 2)
check("unselected variant content stays out", var_stage.has_prim("/Model/low_child"), False)

# The composed set subscripts to variant content, which is the one thing it could
# not reach before: a prim inside a variant has no absolute stage path, so there
# is no composed view to hand back and content is shaped as stored data. pxr
# takes two steps to the same place (GetVariantEditTarget + UsdEditContext).
composed_lod = model.variant_sets["lod"]
check_true("subscript returns stored content", composed_lod["high"].is_variant)
check_true("it is the same node the spec holds", composed_lod["high"] is var_lod["high"])
check("its children are reachable", composed_lod["high"].child_names, ["high_child"])
# A miss declares the variant rather than raising, the same lazy contract the
# container one level up follows for a set that does not compose.
composed_lod["mid"]
check("a new variant composes as empty", composed_lod.variant_names(), ["high", "low", "mid"])
check_true("and it is authored", '"mid"' in var_layer.to_str())
check_true("but composes no children", not var_stage.has_prim("/Model/mid/anything"))
del composed_lod["mid"]
check("deleting it again", composed_lod.variant_names(), ["high", "low"])
check_true("and the layer no longer holds it", '"mid"' not in var_layer.to_str())
# Authoring through the composed handle lands on the same spec the layer holds.
composed_lod["high"].def_(Xform, "authored_via_handle").level = 9
check_true(
    "content authored via the handle composes",
    var_stage.has_prim("/Model/authored_via_handle"),
)
check(
    "and carries its value",
    var_stage["/Model/authored_via_handle"].level.get(),
    9,
)

model.variant_sets["lod"].select_variant("low")
var_stage.invalidate()
check("variant switch resolves", var_stage["/Model/low_child"].level.get(), 1)
check("and drops the variant it replaced", var_stage.has_prim("/Model/high_child"), False)

# --- composed variant sets across layers -----------------------------------
# The composed view reads across the layer stack, the way pxr's UsdVariantSets
# does: a set declared only in a weak layer is still a set of the prim, and the
# selection is the strongest authored opinion. Reads must not create anything --
# the stored __getitem__ creates lazily, so the composed view goes around it.
variant_weak = Layer("smoke_variants_weak.usda")
variant_weak_model = variant_weak.def_(Xform, "/M")
weak_lod = variant_weak_model.authored_prim.variant_sets["lod"]
weak_lod["high"].def_(Xform, "weak_high").level = 2
weak_lod["low"].def_(Xform, "weak_low").level = 1
variant_weak_model.variant_sets["lod"].select_variant("high")

variant_root = Layer("smoke_variants_root.usda")
variant_root_stage = Stage(variant_root)
root_model = variant_root_stage.def_(Xform, "/M")
variant_root.include(variant_weak)
variant_prim = variant_root_stage["/M"]

check("weak-layer set is composed", len(variant_prim.variant_sets), 1)
check_true("and contains the name", "lod" in variant_prim.variant_sets)
check("composed selection crosses layers", variant_prim.variant_sets["lod"].selection, "high")
composed_set = variant_prim.variant_sets["lod"]
check("composed set name", composed_set.name, "lod")
check("composed variant names", composed_set.variant_names(), ["high", "low"])
check("composed set selection", composed_set.selection, "high")
check_true("composed set contains variant", "high" in composed_set)
check_true(
    "the weak layer's chosen variant is the composed content",
    variant_root_stage.has_prim("/M/weak_high"),
)

before = variant_root.to_str()
composed_set.selection
variant_prim.variant_sets["lod"].selection
variant_prim.variant_sets.all_variant_selections()
list(variant_prim.variant_sets)
len(variant_prim.variant_sets)
check_true("reads leave the edit layer alone", variant_root.to_str() == before)
check(
    "all variant selections reports authored sets",
    variant_prim.variant_sets.all_variant_selections(),
    {"lod": "high"},
)

# A key nothing composes is an authoring request, not a miss: __getitem__ creates
# the set in the edit layer so the handle has something to author into. A key
# some layer declares is a read, as checked above.
new_set = variant_prim.variant_sets["brand_new"]
check("new set is composed after creation", "brand_new" in variant_prim.variant_sets, True)
check_true("new set is authored in the edit layer", "brand_new" in variant_root.to_str())
# get is the non-creating lookup, and that is the whole point of it: asking a
# question through __getitem__ would author the answer into the edit layer. It
# raises rather than answering None, so the "does it exist" question that must not
# raise is __contains__. The snapshot is taken here because brand_new above already
# changed the text.
get_snapshot = variant_root.to_str()
check_true(
    "get finds a composed set without authoring",
    variant_prim.variant_sets.get("lod") is not None,
)
check_true(
    "and leaves the layer alone while doing it",
    variant_root.to_str() == get_snapshot,
)
try:
    variant_prim.variant_sets.get("nope")
    get_miss = "returned"
except KeyError:
    get_miss = "raised KeyError"

check("get raises for an undeclared set", get_miss, "raised KeyError")
check_true(
    "and that answer authored nothing",
    "nope" not in variant_root.to_str(),
)
check(
    "membership answers the same question without raising",
    "nope" in variant_prim.variant_sets,
    False,
)
# Declaring a set is not selecting a variant in it, which is exactly why pxr's own
# dictionary keys on the authored selection rather than on the declared sets.
check(
    "a merely declared set has no selection to report",
    variant_prim.variant_sets.all_variant_selections(),
    {"lod": "high"},
)

# --- one composed selection decides the content -----------------------------
# A selection is a composed field, not a per-layer choice: the strongest authored
# one decides, and then that variant's content is composed from every layer that
# holds it. Taking each layer's own choice instead composes two variants' content
# at once, which is what a strong layer switching a weak layer's variant used to do.
root_lod = root_model.authored_prim.variant_sets["lod"]
root_lod["low"].def_(Xform, "root_low").level = 3
composed_set.select_variant("low")
check("the stronger selection wins", variant_prim.variant_sets["lod"].selection, "low")
check_true(
    "select through the composed set authors the selection",
    'string lod = "low"' in variant_root.to_str(),
)
check_true(
    "content comes from the weak layer too",
    variant_root_stage.has_prim("/M/weak_low"),
)
check_true(
    "and from the layer that chose it",
    variant_root_stage.has_prim("/M/root_low"),
)
check(
    "while the weak layer's own choice is dropped",
    variant_root_stage.has_prim("/M/weak_high"),
    False,
)
# Clearing drops this layer's opinion, so the weak layer decides again. Blocking
# authors an empty selection, which is an opinion and stops the weak layer -- the
# two must not be spelled the same way, or one of them silently loses.
composed_set.block_selection()
check("blocking is an authored empty selection", composed_set.selection, "")
check(
    "and is reported rather than left out",
    variant_prim.variant_sets.all_variant_selections(),
    {"lod": ""},
)
check(
    "blocked selection stops the weak layer",
    variant_root_stage.has_prim("/M/weak_low"),
    False,
)
check(
    "and this layer's own content",
    variant_root_stage.has_prim("/M/root_low"),
    False,
)
blocked_text = variant_root.to_str()
check_true("block is written as an empty selection", 'string lod = ""' in blocked_text)

composed_set.clear_selection()
check("clearing lets the weak layer decide again", composed_set.selection, "high")
check_true("and its content composes", variant_root_stage.has_prim("/M/weak_high"))

# all_variant_selections walks the specs itself rather than subscripting each name,
# which removed a prim_index call per set. Walking has to keep picking the strongest
# opinion per set name, so these pin the two directions the loop could get wrong: a
# strong opinion must not be displaced by a weak one (selected twice here, first with
# the root silent and then with it selecting), and a set nobody selected stays out --
# which is what makes the dictionary keyed on an authored selection rather than on a
# declared set.
composed_set.select_variant("low")
check(
    "all selections agrees with the per-set resolution",
    variant_prim.variant_sets.all_variant_selections(),
    {"lod": "low"},
)
check(
    "and so does the set itself",
    variant_prim.variant_sets["lod"].selection,
    "low",
)
declared_only = variant_prim.variant_sets["declared_weak"]
declared_only["a"].def_(Xform, "weak_a")
check(
    "a set selected nowhere is still absent",
    variant_prim.variant_sets.all_variant_selections(),
    {"lod": "low"},
)

# --- the stored lookup raises on a miss, membership is how to ask -------------
# VariantSetSpec.variant() and VariantSetsSpec.variant_set() are reads that raise
# KeyError when this layer does not hold the name, which is why the composition
# engine tests membership before asking: a contributing layer need not declare the
# set, nor hold the selected variant, and walking the stack is asking each one in
# turn. Engine._stored_variant's entry point used to call a VariantSetsSpec.get
# that does not exist, so it failed for every input.
ghost_spec = PrimSpec("Ghost")
ghost_sets = ghost_spec._variant_sets
ghost_sets["lod"]["high"]                                  # declares one variant
check_true(
    "stored set holds the variant it declared",
    ghost_sets["lod"].variant("high") is not None,
)
check(
    "membership answers for one it does not hold",
    "ghost" in ghost_sets["lod"],
    False,
)
check(
    "and the set itself",
    "ghost" in ghost_sets,
    False,
)
check(
    "a selection can name a variant this layer never stored",
    "ghost" in ghost_sets["lod"],
    False,
)
check(
    "and the engine reaches the same answer",
    CompositionEngine._stored_variant(ghost_spec, "lod", "ghost"),
    None,
)
check_true(
    "and finds one that is stored",
    CompositionEngine._stored_variant(ghost_spec, "lod", "high") is not None,
)
check(
    "and reports an undeclared set as absent",
    CompositionEngine._stored_variant(ghost_spec, "nope", "high"),
    None,
)

# The composed side answers the same question without touching storage directly.
check(
    "composed variant_names is the composed union",
    sorted(composed_set.variant_names()),
    ["high", "low"],
)
check(
    "and contains agrees with it",
    "ghost" in composed_set,
    False,
)
check_true(
    "a composed set reads the variant the stack holds",
    variant_prim.variant_sets["declared_weak"].variant("a") is not None,
)
composed_set.clear_selection()

# The parse side has to restore a block as an opinion. An empty name used to reach
# the stored __getitem__, and PrimSpec.__init__ substitutes its own class name for
# an empty one, so `string lod = ""` came back as a variant called "PrimSpec".
blocked_dir = Path(tempfile.mkdtemp())
(blocked_dir / "blocked_variants.usda").write_text(blocked_text, encoding="utf-8")
blocked_roundtrip = Stage(str(blocked_dir / "blocked_variants.usda"))
check(
    "blocked variant selection round trips",
    blocked_roundtrip["/M"].variant_sets["lod"].selection,
    "",
)
check(
    "and invents no variant for the empty selection",
    "PrimSpec" in blocked_roundtrip["/M"].variant_sets["lod"],
    False,
)

# A selection is a field of its own, so it may name a variant nothing declares --
# pxr keeps the two apart, and materialising a variant here would invent content.
ghost_layer = Layer("smoke_variant_ghost.usda", new=True)
ghost_stage = Stage(ghost_layer)
ghost_stage.def_(Xform, "/M").variant_sets["lod"].select_variant("ghost")
ghost_text = ghost_layer.to_str()
check_true(
    "selecting an undeclared variant records the selection",
    'string lod = "ghost"' in ghost_text,
)
check(
    "but authors no variant for it",
    '"ghost" {' in ghost_text,
    False,
)
check(
    "and the set reports no such variant",
    ghost_stage["/M"].variant_sets["lod"].variant_names(),
    [],
)

# --- variant selections across composition arcs -----------------------------
# A selection is a field of the composed prim, so a stronger layer's choice has to
# reach variant content that lives behind an arc -- and a block has to stop it
# rather than fall through to the file it points at. Every expectation below was
# read off the reference implementation over the same files; the interpreter this
# script normally runs under has no pxr, so they are literal here.
# workspace/probe_variant_arcs.py is the same comparison done live.
ARC_ASSET = """#usda 1.0
def Xform "Model" (
    variants = {
        string lod = "high"
    }
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            def Xform "high_geo"
            {
            }
        }
        "low" {
            def Xform "low_geo"
            {
            }
        }
    }
}
"""


def arc_shot(arc, selection=None):
    """One prim reaching the asset through ``arc``, optionally choosing a variant."""
    lines = ['#usda 1.0', 'def Xform "Asset" (']
    if selection is not None:
        lines += ["    variants = {", f'        string lod = "{selection}"', "    }"]
    lines += ['    prepend variantSets = "lod"', f"    {arc}", ")", "{", "}"]
    return "\n".join(lines) + "\n"


# (arc, selection on the referencing prim, expected selection, expected children,
#  high_geo present, low_geo present)
ARC_CASES = [
    ("reference picks the other variant",
     "references = @asset.usda@</Model>", "low", "low", ["low_geo"], False, True),
    ("reference with no opinion lets the file decide",
     "references = @asset.usda@</Model>", None, "high", ["high_geo"], True, False),
    ("block stops the referenced selection",
     "references = @asset.usda@</Model>", "", "", [], False, False),
    ("payload picks the other variant",
     "payload = @asset.usda@</Model>", "low", "low", ["low_geo"], False, True),
]

for label, arc, selection, expected_selection, expected_children, has_high, has_low in ARC_CASES:
    arc_dir = Path(tempfile.mkdtemp())
    (arc_dir / "asset.usda").write_text(ARC_ASSET, encoding="utf-8")
    (arc_dir / "shot.usda").write_text(arc_shot(arc, selection), encoding="utf-8")
    arc_stage = Stage(str(arc_dir / "shot.usda"))
    arc_prim = arc_stage["/Asset"]
    check(f"{label}: selection", arc_prim.variant_sets["lod"].selection or "", expected_selection)
    check(f"{label}: children", sorted(arc_prim.child_names), expected_children)
    check(f"{label}: high_geo", arc_stage.has_prim("/Asset/high_geo"), has_high)
    check(f"{label}: low_geo", arc_stage.has_prim("/Asset/low_geo"), has_low)

# Two references deep: the outermost opinion is the one that decides, and the
# middle file's own selection must not pull its variant back in.
nested_dir = Path(tempfile.mkdtemp())
(nested_dir / "asset.usda").write_text(ARC_ASSET, encoding="utf-8")
(nested_dir / "mid.usda").write_text(
    '#usda 1.0\ndef Xform "Mid" (\n'
    "    variants = {\n        string lod = \"high\"\n    }\n"
    '    prepend variantSets = "lod"\n'
    "    references = @asset.usda@</Model>\n)\n{\n}\n",
    encoding="utf-8",
)
(nested_dir / "shot.usda").write_text(
    arc_shot("references = @mid.usda@</Mid>", "low"), encoding="utf-8"
)
nested_stage = Stage(str(nested_dir / "shot.usda"))
check(
    "nested reference: selection",
    nested_stage["/Asset"].variant_sets["lod"].selection,
    "low",
)
check("nested reference: children", sorted(nested_stage["/Asset"].child_names), ["low_geo"])
check("nested reference: high_geo", nested_stage.has_prim("/Asset/high_geo"), False)
check("nested reference: low_geo", nested_stage.has_prim("/Asset/low_geo"), True)

# An inherited class may carry both the variant set and its content, and the
# inheriting prim's own selection still wins over the class's.
inherit_dir = Path(tempfile.mkdtemp())
(inherit_dir / "shot.usda").write_text(
    '#usda 1.0\nclass Xform "Base" (\n'
    "    variants = {\n        string lod = \"high\"\n    }\n"
    '    prepend variantSets = "lod"\n)\n{\n'
    '    variantSet "lod" = {\n'
    '        "high" {\n            def Xform "high_geo"\n            {\n            }\n        }\n'
    '        "low" {\n            def Xform "low_geo"\n            {\n            }\n        }\n'
    "    }\n}\n\n"
    'def Xform "Asset" (\n'
    "    variants = {\n        string lod = \"low\"\n    }\n"
    '    prepend variantSets = "lod"\n    inherits = </Base>\n)\n{\n}\n',
    encoding="utf-8",
)
inherit_stage = Stage(str(inherit_dir / "shot.usda"))
check(
    "inherit: selection",
    inherit_stage["/Asset"].variant_sets["lod"].selection,
    "low",
)
check("inherit: children", sorted(inherit_stage["/Asset"].child_names), ["low_geo"])
check("inherit: high_geo", inherit_stage.has_prim("/Asset/high_geo"), False)
check("inherit: low_geo", inherit_stage.has_prim("/Asset/low_geo"), True)

# --- relocates ------------------------------------------------------------
rel_layer = Layer("smoke_relocate.usda")
old = rel_layer.def_(Xform, "/Old")
old.moved = 1
rel_layer.relocate("/Old", "/New")

rel_stage = Stage(rel_layer)
check("relocate hides source", rel_stage.has_prim("/Old"), False)
check("relocate exposes target", rel_stage.has_prim("/New"), True)
check("relocated value readable", rel_stage["/New"].moved.get(), 1)
# Removing the arc puts the prim back where it was. The method is spelled
# remove_relocate; it used to be remove_relacate, and nothing called it, so the
# typo went unnoticed until the two spellings were compared side by side.
rel_layer.remove_relocate("/Old")
rel_stage.invalidate()
check("removed relocate restores the source", rel_stage.has_prim("/Old"), True)
check("and withdraws the target", rel_stage.has_prim("/New"), False)
check("the value is reachable again", rel_stage["/Old"].moved.get(), 1)
check_true("the arc is gone from the layer", "relocates" not in rel_layer.to_str())

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
# The attribute and the get_/set_ pair are two spellings of one thing, and the
# get_/set_ pair owns the behaviour; targets is a thin alias over it. They must
# agree in both directions or the alias has silently forked.
check("both spellings read alike", rel2_src.link.get_targets(), rel2_src.link.targets)
rel2_src.link.set_targets(["</Target>"])
check("set_targets is what targets reads", rel2_src.link.targets, ["</Target>"])
rel2_src.link.targets = ["</Target>"]
check("the setter is the same write", rel2_src.link.get_targets(), ["</Target>"])

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

# --- stage flatten (to_str) ------------------------------------------------
# The flattened text must describe the same composed scene with no arc left to
# resolve: sub-layers, references and variants are inlined, and only authored
# opinions survive. Parsing the text back has to answer the same values.
flatten_ref = Layer("flatten_ref.usda")
flatten_ref_stage = Stage(flatten_ref)
flatten_ref_stage.def_(Sphere, "/Inner")
flatten_ref_stage["/Inner"].radius = 3.0
flatten_ref_stage.default_prim = "/Inner"

flatten_base = Layer("flatten_base.usda")
flatten_base_stage = Stage(flatten_base)
flatten_base_stage.def_(Xform, "/Model")
flatten_base_stage["/Model"].mass = 1.0
flatten_base_stage["/Model"].metadata.doc = "base doc"
flatten_over = Layer("flatten_over.usda")
flatten_over_stage = Stage(flatten_over)
flatten_over_stage.def_(Xform, "/Model")
flatten_over_stage["/Model"].mass = 2.0
flatten_over_stage["/Model"].note = "from override"
flatten_base.include(flatten_over, prepend=False)

flatten_root = Layer("flatten_root.usda")
flatten_root_stage = Stage(flatten_root)
flatten_root_stage.def_(Xform, "/Model")
flatten_root_stage["/Model"].mass = 3.0
flatten_root.include(flatten_base)
flatten_root_stage["/Model"].metadata.author = "me"
model_spec = flatten_root_stage["/Model"].authored_prim
flatten_high = model_spec.variant_sets["lod"]["high"]
flatten_high.def_(Xform, "high_child").level = 2
flatten_root_stage["/Model"].variant_sets["lod"].select_variant("high")
flatten_root_stage["/Model"].reference(flatten_ref)
flatten_root_stage.over_("/Extra").reference(flatten_ref)
flatten_root_stage.default_prim = "/Model"

flat_text = flatten_root_stage.to_str()
check_true("flatten header", flat_text.startswith("#usda 1.0"))
check_true("flatten drops subLayers", "subLayers" not in flat_text)
check_true("flatten drops references", "references" not in flat_text)
check_true("flatten drops variantSet", "variantSet" not in flat_text)
# The selected variant's content is composed content, so it is written as plain
# prims; the selection itself is a field with no arc left to point at.
check_true("flatten drops the variant selection", "variants" not in flat_text)
check_true("flatten inlines the selected variant", 'def Xform "high_child"' in flat_text)
check_true("flatten keeps composed typeName", 'def Xform "Model"' in flat_text)
# Specifiers compose by kind, not layer strength: def > class > over across all
# contributing specs. An over that references a def must flatten to def -- that
# is what keeps a flattened reference chain readable -- and the composed typeName
# comes with it.
check_true("over with a reference flattens to def", 'def Sphere "Extra"' in flat_text)
check_true("no over survives flatten", "\nover " not in flat_text)

flat_dir = Path(tempfile.mkdtemp())
flat_file = flat_dir / "flattened.usda"
flat_file.write_text(flat_text, encoding="utf-8")
flat_stage = Stage(str(flat_file))
check("flattened mass is the root opinion", flat_stage["/Model"].mass.get(), 3.0)
check("flattened override opinion", flat_stage["/Model"].note.get(), "from override")
check("flattened composed doc", flat_stage["/Model"].metadata.get("doc"), "base doc")
check("flattened custom data", flat_stage["/Model"].metadata.get("author"), "me")
check("flattened defaultPrim", flat_stage.metadata.get("defaultPrim"), "Model")
check("flattened variant child", flat_stage["/Model/high_child"].level.get(), 2)
check_true("flattened stage is Xform", isinstance(flat_stage["/Model"], Xform))
# A reference composes into the referencing prim itself: the Sphere's authored
# radius shows up as /Model's own opinion, not under a child.
check(
    "flattened reference inlines into the referencing prim",
    flat_stage["/Model"].radius.get(),
    3.0,
)

# --- traverse and active ---------------------------------------------------
# active is USD's built-in deactivation field. The composition engine stays
# active-blind -- inactive prims stay composed and reachable by path -- so
# deactivation is a traversal-time decision: traverse() prunes an inactive prim
# together with its subtree, traverse(all=True) is pxr's TraverseAll.
active_base = Layer("smoke_active_base.usda")
active_base_stage = Stage(active_base)
active_base_stage.def_(Xform, "/Alive")
active_base_stage["/Alive"].mark = 1
active_base_stage.def_(Xform, "/Dead")
active_base_stage["/Dead"].metadata.active = False
active_base_stage.def_(Xform, "/Dead/Hidden")
active_base_stage["/Dead/Hidden"].mark = 3

active_root = Layer("smoke_active_root.usda")
active_root_stage = Stage(active_root)
active_root_stage.def_(Xform, "/Barely")
active_root_stage["/Barely"].mark = 5
active_root.include(active_base)

active_stage = Stage(active_root)
check(
    "traverse prunes inactive subtrees",
    [p.path for p in active_stage.traverse()],
    ["/Alive", "/Barely"],
)
check(
    "traverse(all) visits everything",
    [p.path for p in active_stage.traverse(all=True)],
    ["/Alive", "/Dead", "/Dead/Hidden", "/Barely"],
)
check("inactive start prunes itself", list(active_stage.traverse("/Dead")), [])
check(
    "inactive start traverses with all",
    [p.path for p in active_stage.traverse("/Dead", all=True)],
    ["/Dead", "/Dead/Hidden"],
)
check(
    "prim traverse prunes inactive self",
    [p.path for p in active_stage["/Dead"].traverse()],
    [],
)
check(
    "prim traverse(all) includes inactive self",
    [p.path for p in active_stage["/Dead"].traverse(all=True)],
    ["/Dead", "/Dead/Hidden"],
)
check(
    "prim traverse yields self then subtree",
    [p.path for p in active_stage["/Alive"].traverse()],
    ["/Alive"],
)
check(
    "layer traverse is file scoped",
    [p.path for p in active_root.traverse()],
    ["/Alive", "/Barely"],
)
check(
    "layer traverse(all) is file scoped",
    [p.path for p in active_base.traverse(all=True)],
    ["/Alive", "/Dead", "/Dead/Hidden"],
)
active_root_stage["/Dead"].metadata.active = True
check(
    "stronger active=True revives",
    [p.path for p in active_stage.traverse()],
    ["/Alive", "/Dead", "/Dead/Hidden", "/Barely"],
)
check(
    "layer sees the revived subtree",
    [p.path for p in active_root.traverse()],
    ["/Alive", "/Dead", "/Dead/Hidden", "/Barely"],
)

base_text = active_base.to_str()
check_true("active is a top-level field", "active = false" in base_text)
check_true("and not customData", "customData" not in base_text)
active_dir = Path(tempfile.mkdtemp())
# Both layers go into one directory: the root layer's text carries a relative
# arc to the base layer, which only resolves beside it.
(active_dir / "smoke_active_base.usda").write_text(base_text, encoding="utf-8")
(active_dir / "smoke_active_root.usda").write_text(active_root.to_str(), encoding="utf-8")
active_roundtrip = Stage(str(active_dir / "smoke_active_root.usda"))
check(
    "active survives a round trip",
    [p.path for p in active_roundtrip.traverse()],
    ["/Alive", "/Dead", "/Dead/Hidden", "/Barely"],
)

# --- cleared and blocked attributes ----------------------------------------
# pxr has two operations and pyusd now mirrors both. clear() is pxr's Clear():
# the authored value goes away, the spec survives as a bare declaration, and
# weaker opinions compose through. block() is pxr's Block(): an opinion with no
# value that stops weaker layers, spelled `= None` in the text. Swapping the two
# spellings loses information: writing a block bare would drop it on re-parse,
# and parsing a bare declaration as anything authored would invent an opinion.
block_base = Layer("block_base.usda")
block_base_stage = Stage(block_base)
block_base_stage.def_(Xform, "/A")
block_base_stage["/A"].mass = 5.0

block_root = Layer("block_root.usda")
block_root_stage = Stage(block_root)
block_root_stage.def_(Xform, "/A")
block_root_stage["/A"].mass = 1.0
block_root_stage["/A"].vol = 2.0
block_root.include(block_base)

block_root_stage["/A"].mass.block()
check("block stops the weaker layer", block_root_stage["/A"].mass.get(), None)
block_text = block_root.to_str()
check_true("block is written as = None", "= None" in block_text)
block_dir = Path(tempfile.mkdtemp())
(block_dir / "block_base.usda").write_text(block_base.to_str(), encoding="utf-8")
(block_dir / "block_root.usda").write_text(block_text, encoding="utf-8")
block_roundtrip = Stage(str(block_dir / "block_root.usda"))
check("block survives a round trip", block_roundtrip["/A"].mass.get(), None)
check("authored sibling unaffected", block_roundtrip["/A"].vol.get(), 2.0)
block_spec = block_roundtrip.root_layer.prim_spec_at("/A")
check(
    "parsed block state is Cleared",
    block_spec._props["mass"].value_state,
    PropertySpec.ValueState.Cleared,
)

block_root_stage["/A"].mass.clear()
check("clear lets the weaker value through", block_root_stage["/A"].mass.get(), 5.0)
check_true(
    "clear is written as a bare declaration",
    "custom double mass\n" in block_root.to_str() and "= None" not in block_root.to_str(),
)
(block_dir / "block_root_cleared.usda").write_text(block_root.to_str(), encoding="utf-8")
block_roundtrip = Stage(str(block_dir / "block_root_cleared.usda"))
check("cleared state survives a round trip", block_roundtrip["/A"].mass.get(), 5.0)
cleared_spec = block_roundtrip.root_layer.prim_spec_at("/A")
check(
    "parsed clear state is NotAuthored",
    cleared_spec._props["mass"].value_state,
    PropertySpec.ValueState.NotAuthored,
)

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s):")
    for failure in FAILURES:
        print(f"  {failure}")
    raise SystemExit(1)

print("all smoke checks passed")
