# Repository Guidelines

## Project Structure & Module Organization

- `pyusd/` is the installable package. Core USD objects and parsers live at the package root: `stage.py` (composed stage and edit target), `prim.py` (the prim view), `prim_spec.py` (one layer's stored opinion), `layer.py`, `attribute.py`, and the serializer/parser modules.
- Namespaces such as `pyusd.geom`, `pyusd.physics`, `pyusd.render`, `pyusd.shade`, `pyusd.skel`, and `pyusd.gf` contain hand-written and schema-generated APIs. Keep `.py`, `.pyi`, and schema changes synchronized.
- `workspace/` contains development utilities, smoke tests, code-generation scripts, and runnable examples. `_assets/` stores small USDA fixtures and generated example output.
- `openusd_core_spec/` is the Git submodule containing AOUSD specifications; initialize it when documentation or schema behavior requires it.

## Architecture Notes

`Layer` and `Stage` both hand out `Prim` (and schema subclasses of it). A `Prim` is
always a view bound to `(stage, path)`; `Layer.stage` is a lazily created
single-layer stage whose edit target is that layer, so the two sides share one code
path and neither needs a bound/unbound mode.

- `pyusd/schema_registry.py` maps a `typeName` to its class, inheritance chain, and
  property declarations. It is the single source of truth for what a type looks
  like, built once from the `pyusd` package. Declarations are stripped from the
  classes so a schema class is a pure type marker; `Prim.__new__` dispatches on
  `typeName` so `stage["/M"]` is a `Mesh` and `isinstance` works.
- `pyusd/prim_spec.py` holds `PrimSpec`, the internal materialised form of one layer's
  opinion. It is not exported from `pyusd`; reach it through `Prim.resolved_prim`,
  `Prim.authored_prim`, or `Layer.prim_spec_at` when an operation has to shape
  stored data rather than the composed result.
- Stored properties are `PropertySpec` and its subclasses `AttributeSpec` and
  `RelationshipSpec`, in `property_spec.py`, `attribute_spec.py`, and
  `relationship_spec.py`. They are what a layer serialises and what
  `PrimSpec._props` holds. The names `Property`, `Attribute`, and `Relationship`
  belong to the composed handles in `property.py`, `attribute.py`, and
  `relationship.py` -- USD's own split, `Usd.Attribute` versus
  `Sdf.AttributeSpec` -- so a prim attribute and a stored spec are never confused
  for one another.
- `Property.wrap` is the single place that decides which handle a name means: it
  looks at the resolved spec and returns a `Relationship` only for a
  `RelationshipSpec`, otherwise an `Attribute`. A name nothing declares and
  nothing authored still becomes an `Attribute` with `exists == False`, matching
  `pxr`, where `prim.GetAttribute(name)` returns an invalid `Usd.Attribute`
  rather than `None` -- that is what lets `prim.radius = 5` work on a property
  nobody has heard of yet. `is_valid()` is the pxr spelling of `exists`.
- `Property.__getattr__` allows member access in exactly two cases: the resolved
  spec owns the child, which is the nested-schema case (`xformOp.translate`, and
  authoring through it is what maintains `xformOpOrder`), or the prim's type
  declares the child, which is what makes `prim.exposure.iso` reachable on a
  fresh `Camera` that no layer has materialised. Anything else raises
  `AttributeError`, because a plain attribute has no members and `prim.radius.foo`
  is a typo rather than a request for a property named `radius:foo`.
- The arithmetic a property used to support is shared, not inherited. `Data` cannot be a
  base of the composed `Attribute`, because `Data` owns a stored value: `_value` is an
  instance field there and a method on the handle, `__iadd__` rewrites `self.value`
  rather than authoring an opinion, and `__getattr__` forwards to the value where a
  handle has to read a child property or raise. `isinstance(x, Data)` is also live
  dispatch in five places (`_convert_from`, `_other_value`, `UsdaSerializer`,
  `infer_type`, and `Attribute._other_value`), so inheriting it would make a composed
  handle pass as a stored value. What the two genuinely have in common is the
  arithmetic, so that lives in `_Arithmetic` in `data.py`: a stateless mixin over three
  hooks, `_read()`, `_write(value)` and `_other_value(operand)`. `Data` reads its own
  field and writes itself; `Attribute` reads composition and authors the edit layer.
  The in-place operators end in `_write`, which is the entire behavioural difference.
  Equality is deliberately not in the mixin -- `Data` and `Property` each already have
  one and they agree -- and neither is `__setitem__`, which mutates a value in place and
  so cannot mean anything for one composed out of a layer stack.
  `workspace/test_prim_view.py` asserts `Attribute.__add__ is AttributeSpec.__add__`, so
  a second copy cannot creep back in unnoticed.
- An augmented assignment on a property finishes by assigning the operator's
  result back, and `__iadd__` returns `self`. `Stage._set_property` therefore
  unwraps a `Property` handed to it, so `prim.radius = other.radius` and
  `prim.radius += 1` both mean "that value" rather than "author a handle".
- Metadata and variant views live in `stage_metadata.py` and
  `stage_variant_sets.py`, mirroring their `Stage*` classes.
- The composition engine reads storage nodes directly, so it needs the in-layer
  path and the raw authored arcs, neither of which a composed view can express.
- Variants are the exception: a prim inside a variant has no absolute stage path, so
  variant authoring goes through `Prim.variant_sets` onto the spec.

## Build, Test, and Development Commands

Create or activate a Python 3.7+ virtual environment, then install the package and development tools:

```powershell
python -m pip install -e ".[dev]"
```

Useful checks and workflows:

- `python static_check.py` runs the repository static checks: `compileall -q pyusd`,
  `ruff check --fix --unsafe-fixes .`, then `ty check .`. All three pass clean, and the
  script exits 0. When a reported file is generated, fix `code_generator.py` and
  regenerate; when it is hand-written, fix the file directly. Do not silence findings
  with `per-file-ignores` or a type-check baseline.
- **A module must not ship both a `.py` and a `.pyi`.** When it does, `ty` treats the
  two declarations of the same class as distinct nominal types, so passing an instance
  from the implementation to a parameter annotated with the stub is an
  `invalid-argument-type` error even though the code is correct. This cost 5 findings in
  `prim.py` for as long as `prim.pyi` existed, and `ty` has no setting to merge the two
  views. Seven core stubs were therefore removed: `metadata`, `prim_spec`, `stage`,
  `stage_metadata`, `stage_property`, `stage_variant_sets`, and `prim`. Two core stubs
  remain and are load-bearing: `layer_metadata` and `prim_metadata`, whose
  implementations are empty `class X(Metadata): pass` shells whose only declarations
  live in the stub. Do not add a `.pyi` next to a `.py` that already declares
  everything; that reintroduces the split. The generator enforces this in both
  directions now: `_generate_class_file` refuses to overwrite hand-written
  implementations, and `_regenerate_pyi_file` refuses to write a stub beside one.
  The stub guard has to test the sibling `.py` rather than the stub itself, because
  52 generated stubs carry property getters whose body is a docstring.
- API schema accessors are generated into `pyusd/prim.py`, between the
  `generated api imports` and `generated api accessors` marker pairs. They used to be
  declared in a `pyusd/prim.pyi`; that stub is what kept the duplicate-`Prim` problem
  above alive, and it was the only stub left doing so. They are now **declarations with
  no body, inside an `if TYPE_CHECKING:` block in the class body**. That is what lets
  `Prim.__getattr__` stay the single runtime path -- the class simply has no such
  attributes, so every `*_api` read still falls through to the registry route -- while a
  type checker and an IDE still see all 41 members. The imports they annotate already
  live in the module-level `TYPE_CHECKING` block above the class.
  They were forwarders with bodies at first, which was 41 three-line reimplementations
  of a path that already existed. Moving them to a `.pyi` instead was measured and
  rejected: a stub **replaces** the module for importers rather than adding to it, so
  `prim.pyi` would have had to re-declare all 68 public members of `Prim` -- a `class
  Prim(Any)` stub made `stage`, `prop_names` and `def_` resolve to `Unknown` -- and even
  a complete one left six unavoidable `Prim@pyusd/prim.py` vs `Prim@pyusd/prim.pyi`
  errors to be whitelisted. `if TYPE_CHECKING` needs no stub, no whitelist, and costs
  nothing at runtime. The `generated api imports` region is separate only because `ruff`
  re-sorts it; both regions come from `_collect_api_accessors`, whose `present` test
  cannot be a substring check against the file -- an accessor named `light_api` is a
  substring of its own import line, so a substring test declares every accessor present
  as soon as its import lands.
- The forwarders used two locals rather than `cast`, because `cast` evaluates its first
  argument and PEP 563 does not evaluate annotations. That is what kept the API classes
  inside `TYPE_CHECKING`; importing them at runtime would create a cycle, since every
  schema class imports `Prim`. It no longer applies now that there are no bodies.

- `_merge_fenced_region` judges presence against the whole file, not the region,
  because `ruff` re-sorts the `TYPE_CHECKING` block and carries the opening marker
  along with the imports it thinks belong before it. Import order is deliberately
  left to `ruff`: the hand-written `from .layer` / `from .stage` imports share that
  block and are not the generator's to move. A missing marker raises rather than
  generating nothing.
- `generate_code.py` omits `pyusd/schema.usda` and `pyusd/geom/schema.usda`, so
  running it does not pick up the core schemas at all. `generate_api_accessors`
  walks up from the schema directory to find `prim.py`, which means the core schema
  finds it in the package root while the namespace schemas find it one level up.
- `_insert_imports` has to place statements after the whole import block, not after
  its first line: the generated stubs wrap long imports in parentheses across several
  lines, and matching on `from ` alone injects the new statement inside the open
  paren. For the same reason `_ensure_import` compares the unparsed statement rather
  than its text.
- Two metadata bugs on that path are worth remembering, because neither had a test.
  `Metadata.update` used to `pop("customData")` out of the caller's dict, and
  `PrimSpec._fetch_from_class` passes a schema class's `meta` dict straight in, so the
  first application of a multiple-apply schema stripped `customData` off the class and
  the second raised `KeyError`. `dictionary.update_one` also called the unbound
  `dictionary.update` on values that were plain dicts. Both are covered in
  `workspace/test_prim_view.py`.
- `Prim.prop_names` reports namespaced property names, and that took two separate fixes
  to get right. It used to filter out every name containing a `:`, which hid every
  namespaced declaration in the package: Gprim's `primvars:displayColor`, Material's
  `outputs:surface`, Camera's `exposure:*` and `shutter:*`. A Material reported nothing
  at all. USD has no such filter. The filter had been added to suppress 19 phantom
  `xformOp:*` leaves that `declared_leaf_names` invented by walking into `xformOp`,
  which is not a namespace group but an `XformOp` instance -- a schema over one op
  attribute. It must not be expanded, and it is not a property name either; the op
  attributes come into being when `AddXformOp` authors them.
- `declared_leaf_names` therefore has three cases, and each one is load-bearing: a
  non-leaf entry whose type is not `Attribute` is a nested schema and is skipped; a
  non-leaf entry typed `dtypes.namespace` is a pure namespace and contributes only its
  children; any other non-leaf entry is also a property in its own right, so its own
  name is reported too. That last case is `UsdGeomCamera`'s legacy top-level `float
  exposure`, which the generated class models as the head of the `exposure:` group --
  without it a Camera reported 21 of pxr's 22 names.
- `_generate_pyi_attribute_signature` drops a member whose name collides with a
  `PropertySpec` attribute -- `name`, `type`, `value`, `path` and the rest -- rather
  than shadowing it in a stub. That is lossy but long-standing, and it is invisible
  until a namespace's *only* member is dropped: the emitted class then has an empty
  body, which is not valid Python. `colorSpace` is exactly that case, since its only
  member is `colorSpace:name`. A namespace stub whose members all vanish is now
  skipped instead of written, so `color_space.pyi` does not exist. Note the two
  "skip" guards test different things: `_generate_namespace_pyi` returning empty means
  there is nothing declarable, while `_holds_hand_written_code` means the sibling
  `.py` is hand-written and must not gain a stub at all.
- Three generator methods used to classify a schema by whether it had an explicit name,
  which is true of nothing arriving from an `#include`: `_determine_base_class` returned
  `APISchemaBase` for all of them, `_determine_schema_kind` returned `NonAppliedAPI`, and
  `_generate_imports` resolved the base through a table assuming every base lives in
  `geom/`, so `geom/xformable.py` imported `..geom.imageable`. All three go by `inherits`
  first now. Regenerating `Imageable`, `Xformable`, `Boundable` or `Gprim` before this
  was fixed would have collapsed the typed hierarchy, and `DistantLight` was not even
  `Xformable`. A base that resolves to a class in the same schema directory is imported
  with a same-directory relative import; the `cross_module_bases` table is only the
  fallback for bases from another namespace.
- `pyusd/api_schema_base.py` and `pyusd/model_api.py` are hand-written but sit where
  `generate_pyclasses` would write, and a full `generate_all` used to replace them with
  a schema dump. `_generate_class_file` now refuses any target that holds real
  executable code and prints what it skipped. The test is that a function body is
  something other than `...`, which a generated class file never has -- so the guard
  needs no list to go stale, and it is scoped to the `.py` path on purpose: 52 of the
  118 generated `.pyi` stubs carry property getters with docstring bodies, so the same
  test would block them.
- Generated modules import the shared core modules from the package root, and that
  relative prefix used to be spelled `..` in 24 places. That is right for a namespace
  directory but escapes the package when the schema *is* the root one: regenerating
  `pyusd/typed.py` produced `from ..common import SchemaKind`. `_package_prefix`
  derives it from the schema directory instead. The core schema is not in
  `generate_code.py` at all, which is why this went unnoticed -- that script's real cost
  is that running it rewrites 243 files, so do not run it as part of an unrelated change.
- A default parsed from a schema **is** emitted into the generated declaration, so a
  property the type declares but no layer authored still reads as what the schema says
  it is. pxr does the same and reports it as un-authored; the fallback at the end of
  `composition.resolve_property` hands out that declaration, so without the value
  `prim.radius` on a fresh Sphere read as `None` and `def Sphere "x"` had no extent.
  An array with no declared default still gets a synthesised `value=[]`, which is
  where pyusd and pxr diverge on `xformOpOrder` -- pxr returns `None` there. That
  divergence is long-standing and deliberate; do not "fix" it as collateral.
  Emitting defaults needed three things, each of which blocked it before:
  - `dtypes.token` was a `ReprEnum` with no members, so `token("default")` raised
    "has no members" and no token-typed default could be constructed. It is a plain
    `str` subclass now, which makes it a usable *base* for the enumerations the
    generator emits for `allowedTokens` -- those ask for `ReprEnum` themselves, and
    `attribute_spec.py` separates them from `token` with `value_type != token` before
    reading member values. `common.py` and `sdf/common.py` hold four such enums by
    hand and were changed by hand.
  - A `token[]` with `allowedTokens` was declared as the bare enum rather than
    `List[Enum]`, because the generator replaced the whole type instead of the
    element type. Invisible while no default was emitted; the default then failed to
    convert. `_generate_imports` cannot see the `List` because it only reads the
    schema's own type name, so `_generate_class_file` and `_generate_pyi_imports`
    add it.
  - `_generate_pyi_imports` has to add `from enum import ReprEnum` whenever the stub
    re-emits an `allowedTokens` enumeration, or `ty` reports it undefined. Same for
    `_generate_namespace_pyi`, and both class-file paths in `_generate_class_file`
    and `_generate_namespace_pyi`.
- A `PropertySpec` with no parent was never installed in a prim, so no layer holds an
  opinion about it. `AttributeSpec.value_state`'s "a non-empty list means authored"
  heuristic has to stop there: it is about a materialised spec whose value arrived
  without going through the setter, and without the guard a schema declaration such as
  `Sphere.extent` reported `Authored` while pxr reports `HasAuthoredValue() == False`.
- `UsdGeomXformable` declares no `xformOp` property -- its ops are authored on demand by
  AddXformOp, which is why pxr reports none of them -- and the schema gives the generator
  nothing to parse, so `xformOp` is not among the parsed attributes of `Xformable`, which
  are just `xformOpOrder`. pyusd exposes the op slots as a nested `XformOp` instead, which
  is what backs `prim.xformOp.translate = ...` and the automatic `xformOpOrder` upkeep.
  That declaration comes from `NESTED_SCHEMA_DECLARATIONS`, and **both** the class-file and
  the stub paths have to consult it. A stub shadows the module it sits beside, so a member
  the `.py` declares and the `.pyi` omits is not untyped, it is *invisible*: attribute
  access falls through to `Prim.__getattr__`, which is `Any`. That is exactly how `xformOp`
  ended up with no type at all while `radius`, `extent` and `xformOpOrder` all had one --
  the declaration was in `xformable.py` the whole time and `xformable.pyi` never had it.
  `workspace/test_prim_view.py` catches the runtime half of this; the static half is why
  the stub emission below is not optional.
- A nested declaration is emitted into a stub as a `@property`, not a bare annotation.
  `PropertySpec` defines `__get__` and `__set__`, so a class attribute annotated with one
  of those *is* a descriptor, and `ty` checks the access against `__get__`'s first
  parameter -- a `PrimSpec`, not the `Prim` that `Prim.__getattr__` hands out. Every other
  member in these stubs is a property for the same reason. The stub also has to import the
  named class, which `_generate_imports` finds for the `.py` from the `XformOp()` assignment
  and a stub, having none, cannot.
- The generator emits imports in its own order and `ruff check --fix` sorts them, so a
  generate-then-lint cycle is only idempotent as a pair. That is why the accessor
  generation above leaves import order to `ruff`.
- Whether a layer reads its file is decided in **two** places, and neither is the
  constructor argument. `Stage.__init__` has a fast path -- a `Layer` is used as is, a
  name is looked up in the process registry first, and `Layer.load` runs only if
  `os.path.exists`. The real decision is `LayerCache.materialize`, which loads a layer
  that is **empty and whose file exists**, and it runs lazily: `Layer("out.usda")` parses
  nothing, and the file's contents appear only on the first prim query. "Loaded" is
  therefore not observable from the constructor.
- `new=True` on `Layer.__init__` and `Stage.__init__` means "never read this file". It
  sets a flag on `LayerImpl` rather than threading a parameter, because `materialize` is
  the path that has to honour it and it only ever sees a `Layer`. The flag is declared on
  `Layer`'s annotation block too, since `Layer.__getattr__` delegates only names in
  annotations. A new layer neither looks up nor registers in `_registry`: an empty
  scratch layer that carries a name is not that file's layer, so sharing or clobbering
  one would be wrong in both directions, and two of them are independent the way two
  anonymous layers are.
- `Layer.load` inside one process hands back the registry's layer instead of re-reading,
  because `Layer.__init__` finds the cached impl first and the parser's `_loaded`
  early-return then short-circuits. One load per path per process;
  `LayerCache.invalidate(file_name)` drops the mtime/size cache for the lazy path.
- A `Prim` is an interned view: `stage["/M"] is stage["/M"]`. The cache lives on
  `StageImpl` and is keyed by `(path, class)` -- keying on the class is what keeps it
  correct with no invalidation hook, since the class comes from the composed typeName,
  so a prim retyped by a stronger layer lands on a different key and the view built for
  its old type is never handed out again. It is per Stage, so `stage` and `layer.stage`
  keep separate caches and stay distinct, which is what the existing `different stages
  differ` check asserts. `__eq__` still compares `(stage is, path)` and still lets a
  view compare equal to its path string; that overload is deliberate and must stay.
  `Prim.__init__` re-runs on a cached object and re-assigns the same two attributes --
  safe only because no schema class overrides `__init__`.
- `prim_index` is not cheap to call twice. Its cache key holds a signature of the whole
  layer stack and a sorted list of unloaded payloads, rebuilt on every lookup, so
  `Stage.__getitem__` resolves existence and typeName together through
  `resolve_view_type_name` and passes the answer down as `_type_name`. Note that
  `__init__` must accept that argument too, because Python passes one call's arguments
  to both `__new__` and `__init__`. Making the key itself revision-cached would remove
  most of the remaining cost and is the obvious next step; it touches all ten
  `prim_index` call sites.

- `pyusd/gf/` carries bool result types alongside the numeric ones: `bool2`, `bool3`,
  `bool4`, `matrix2b`, `matrix3b`, `matrix4b`, and `quatb`. `genType.gen_type` builds
  those module names for a `c_bool` dtype, so an ordering comparison or `funcs.not_`
  cannot work without them. They are deliberately absent from `usd_vector_types` and
  friends in `utils.py`, because USDA has no bool vector type; the classes exist only
  to hold comparison results. Matrices are always square: `genMat.mat_type` reads
  `shape[0]` and ignores the rest, so a `(2, 3)` request silently yields a 2x2.
- Three things about the `gf` layer are load-bearing and easy to get wrong.
  `genType` declares `__len__`/`__getitem__`/`__setitem__`/`__iter__` that raise
  `NotImplementedError`, because every element-wise helper in `funcs.py` is annotated
  against `genType` while only ever receiving `genVec`/`genMat`/`genQuat`; `genMat`
  therefore has to forward `__len__` to `ctypes.Array.__len__` explicitly, since
  `genType` comes first in its MRO and would otherwise shadow it. A `genMat` index
  yields a row, so element access goes through `genMat.at(row, col)` and
  `genMat.put(row, col, value)`, never `m[i, j]` in arithmetic; `__getitem__` has to
  advertise `genVec` for that reason. The `genQuat` w/x/y/z properties are shadowed
  at instance level by the ctypes field descriptor on the concrete subclass, so
  their bodies reach the field through `ctypes.Structure.__getattribute__`.
- `workspace/test_gf_types.py` covers the `gf` layer. Type checking found eight real
  defects there that every other smoke script missed, including `funcs.abs`/`min`/
  `max` going through `__builtins__` (a dict inside an imported module), ordering
  comparisons on vectors and matrices, `matrix *= matrix` silently doing nothing
  because a slice index matched no branch of `__setitem__`, and the four `genQuat`
  field getters. Three more turned up while restoring attribute arithmetic, all of
  them in the element-wise operators and all of them silent until exercised:
  - `_op`, `_rop`, `_compare_op` and `_compare_rop` accepted any operand. An object
    that is neither a number nor a shape-matched `genType` was passed to the
    element function whole, so `double3(...) + attribute` computed a plausible
    result type from the handle's delegated `dtype` and then assigned a whole
    vector into every element. They return `NotImplemented` now, which is what lets
    Python reach the other operand's reflected method; raising `TypeError` there
    stops the fallback instead of enabling it. `_iop` and `_compare_op` keep
    raising, since neither has a reflected form to defer to.
  - All five loops counted slots with `len()`. That is right for a flat `genVec` or
    `genQuat` and wrong for `genMat`, whose `__len__` is ctypes' flat element count
    while `m[i]` is a row -- so `matrix + matrix`, `matrix - matrix` and
    `matrix * 2` raised `IndexError`. `genMat._op` rescues `*` itself, which is why
    matrix multiplication worked and nothing else did; the count is `_slot_count`.
  - `genQuat.__init__` passed `[1, 0, 0, 0]` to `ctypes.Structure.__init__`, which
    wants one positional value per field, so `quatd()` raised "must be real number,
    not list". Every quaternion operator default-constructs its result, so all of
    quaternion arithmetic was dead.
- `genVec3`, `genMat3` and `genQuat` have no `dtype`, and that is by design: they
  are abstract intermediates, and the `dtype`/`math_form`/`shape` they would have to
  guess belong to the concrete subclass. Only instantiate the concrete types
  (`double3`, `matrix4d`, `quatd`), and reach for `gen_type` when the concrete type
  is not known statically.
- Treat a new `gf` finding as a possible bug until proven otherwise.
- `python workspace/test_roundtrip.py` asserts every `_assets/` fixture survives a
  parse/serialize round trip unchanged.
- `python workspace/test_pxr_parity.py` cross-checks composed prim paths, typeNames,
  and property names against the reference implementation. It re-execs itself with
  `.venv\Scripts\python.exe`, because that is where the `pxr` bindings live.
- `python workspace/test_prim_view.py` covers the composed-stage API: shared layer
  identity, typed views, schema fallback, LIVERPS strength, variants, payload state,
  relocates, relationships, and edit layer isolation.
- `python workspace/test_code_generator.py` and `python workspace/test_usdcore.py` run the existing smoke scripts.
- `python workspace/generate_code.py` regenerates schema APIs from the `schema.usda` files. The generator is **not** idempotent (import order and some stubs drift), so do not run it as part of an unrelated change.
- `python workspace/main.py` exercises layer editing and USDA serialization. Example scripts are under `workspace/examples/`.

## Coding Style & Naming Conventions

Use four spaces, double-quoted strings, and the 88-column target configured in `ruff.toml` (with its listed exceptions). Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; and USD schema names as defined by the source schema. Keep public API stubs (`.pyi`) aligned with implementations.

## Testing Guidelines

There is no configured pytest suite or coverage gate. Add focused scripts under `workspace/` (named `test_*.py`) for behavior changes, and run them plus `static_check.py`. Include USDA fixtures in `_assets/` when serialized output needs stable input.

## Commit & Pull Request Guidelines

Existing commits use short, imperative, lowercase summaries (for example, `add relocate method for layer` and `fix with ruff`), without a required prefix. Keep commits focused and mention generated code when applicable. Pull requests should explain the change, identify affected namespaces or schemas, list validation commands, and include USDA output or fixtures for serialization changes. Link an issue when one exists.

## Configuration & Dependencies

Runtime dependencies are declared in `pyproject.toml` (`tree-sitter`, `tree-sitter-usd`, and `beartype`). Use `install_self.py` only when its mirror-specific pip commands are appropriate; prefer the editable install above. Do not commit virtual environments, caches, build output, or unrelated generated artifacts.
