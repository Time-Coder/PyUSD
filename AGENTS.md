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
- Property, metadata, and variant views live in `stage_property.py`,
  `stage_metadata.py`, and `stage_variant_sets.py`, mirroring their `Stage*` classes.
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
  everything; that reintroduces the split.
- API schema accessors are generated into `pyusd/prim.py`, between the
  `generated api imports` and `generated api accessors` marker pairs. They used to be
  declared in a `pyusd/prim.pyi`; that stub is what kept the duplicate-`Prim` problem
  above alive, and it was the only stub left doing so. The accessors are typed
  forwarders onto `PrimSpec.__getattr__`, which stays the single runtime path, and
  `Prim.__getattr__` still routes any `*_api` name to the spec so a schema that
  appears without a regeneration keeps working. Three things about this are load
  bearing and easy to get wrong:
  - The forwarders annotate two locals rather than calling `cast`, because `cast`
    evaluates its first argument and PEP 563 does not evaluate annotations. That is
    what keeps the API classes inside `TYPE_CHECKING`; importing them at runtime
    would create a cycle, since every schema class imports `Prim`.
  - `ty` reads `PrimSpec.__getattr__`'s declared return type through `getattr`, so
    the result is `Property | APISchemaBase | APIWrapper` and is not assignable to
    the schema class directly. The first local is annotated `Any` to absorb that.
  - Whether an item is already present cannot be a substring test against the file.
    An accessor named `light_api` is a substring of its own import line, so a
    substring check declares every accessor present as soon as its import lands.
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
  field getters. Treat a new `gf` finding as a possible bug until proven otherwise.
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
