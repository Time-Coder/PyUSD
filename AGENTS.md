# Repository Guidelines

## Project Structure & Module Organization

- `pyusd/` is the installable package. Core USD objects and parsers live at the package root (`stage.py`, `layer.py`, `prim.py`, `attribute.py`, and serializer/parser modules).
- Namespaces such as `pyusd.geom`, `pyusd.physics`, `pyusd.render`, `pyusd.shade`, `pyusd.skel`, and `pyusd.gf` contain hand-written and schema-generated APIs. Keep `.py`, `.pyi`, and schema changes synchronized.
- `workspace/` contains development utilities, smoke tests, code-generation scripts, and runnable examples. `_assets/` stores small USDA fixtures and generated example output.
- `openusd_core_spec/` is the Git submodule containing AOUSD specifications; initialize it when documentation or schema behavior requires it.

## Build, Test, and Development Commands

Create or activate a Python 3.7+ virtual environment, then install the package and development tools:

```powershell
python -m pip install -e ".[dev]"
```

Useful checks and workflows:

- `python -m ruff check .` runs lint checks; `python ruff_check.py` runs the repository's auto-fixing Ruff wrapper.
- `python -m compileall pyusd workspace` catches syntax errors (and updates ignored `__pycache__` files).
- `python workspace/test_code_generator.py` and `python workspace/test_usdcore.py` run the existing smoke scripts.
- `python workspace/generate_code.py` regenerates schema APIs from the `schema.usda` files; review generated diffs before committing.
- `python workspace/main.py` exercises layer editing and USDA serialization. Example scripts are under `workspace/examples/`.

## Coding Style & Naming Conventions

Use four spaces, double-quoted strings, and the 88-column target configured in `ruff.toml` (with its listed exceptions). Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; and USD schema names as defined by the source schema. Keep public API stubs (`.pyi`) aligned with implementations.

## Testing Guidelines

There is no configured pytest suite or coverage gate. Add focused scripts under `workspace/` (named `test_*.py`) for behavior changes, and run them plus Ruff and `compileall`. Include USDA fixtures in `_assets/` when serialized output needs stable input.

## Commit & Pull Request Guidelines

Existing commits use short, imperative, lowercase summaries (for example, `add relocate method for layer` and `fix with ruff`), without a required prefix. Keep commits focused and mention generated code when applicable. Pull requests should explain the change, identify affected namespaces or schemas, list validation commands, and include USDA output or fixtures for serialization changes. Link an issue when one exists.

## Configuration & Dependencies

Runtime dependencies are declared in `pyproject.toml` (`tree-sitter`, `tree-sitter-usd`, and `typeguard`). Use `install_self.py` only when its mirror-specific pip commands are appropriate; prefer the editable install above. Do not commit virtual environments, caches, build output, or unrelated generated artifacts.
