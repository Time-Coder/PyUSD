import ast
import os
import re
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from beartype import beartype
from tree_sitter import Node

# Sentinel for "every line was blank" while measuring docstring indentation.
_NO_INDENT = 1 << 30


class CodeGenerator:
    # Nested schema declarations that no property declaration in the .usda produces.
    # UsdGeomXformable declares no `xformOp` property: its ops are authored on demand by
    # AddXformOp, which is why UsdPrim reports none of them. pyusd exposes the op slots
    # as a nested XformOp instead, so `prim.xformOp.translate = ...` works and writing
    # an op keeps xformOpOrder up to date. XformOp arrives through an #include, so the
    # parser never sees it as an attribute and the declaration cannot be derived from
    # the schema -- without it, regenerating xformable.py silently drops that authoring
    # API. Keyed by class name, with (attribute, class, module) triples.
    NESTED_SCHEMA_DECLARATIONS = {
        'Xformable': [('xformOp', 'XformOp', 'xformop')],
    }


    gf_types = {
        "bool2", "bool3", "bool4",
        "int2", "int3", "int4",
        "half2", "half3", "half4",
        "float2", "float3", "float4",
        "double2", "double3", "double4",
        "matrix2b", "matrix3b", "matrix4b",
        "matrix2f", "matrix3f", "matrix4f",
        "matrix2d", "matrix3d", "matrix4d",
        "quatb",
        "quatf", "quatd", "quath",
        "color3h", "color3f", "color3d",
        "color4h", "color4f", "color4d",
        "texCoord2h", "texCoord2f", "texCoord2d",
        "texCoord3h", "texCoord3f", "texCoord3d",
        "normal3h", "normal3f", "normal3d",
        "point3h", "point3f", "point3d",
        "vector3h", "vector3f", "vector3d",
        "frame4d"
    }
    dtypes_types = {'double', 'half', 'int64', 'string', 'token', 'pathExpression', 'timecode', 'uchar', 'uint', 'uint64', 'namespace', 'asset', 'dictionary', 'opaque', 'group'}
    # Enums that live in common.py rather than dtypes.py. A property may use one
    # directly (for example UsdPhysics.Axis) without an allowedTokens list, so
    # these have to be imported off the needed-types set like any other type.
    common_types = {'Axis', 'Kind', 'SchemaKind'}

    def __init__(self, schema_path: str):
        """初始化代码生成器

        Args:
            schema_path: schema.usda 文件的路径
        """
        self.schema_path: str = schema_path
        self.schema_dir: str = os.path.dirname(schema_path)
        self.classes_info: Dict[str, Dict[str, Any]] = {}
        self.class_names: List[str] = []
        self._parsed: bool = False  # 标记是否已解析
        self._generated_ns_files: Set[str] = set()  # 已生成的命名空间文件

        # 初始化 parser
        import tree_sitter_usd
        from tree_sitter import Language, Parser

        lang = Language(tree_sitter_usd.language())
        self.parser: Parser = Parser(lang)

    def parse(self) -> None:
        """解析 schema.usda 文件，提取类信息

        如果已经解析过，则跳过解析过程。
        """
        if self._parsed:
            return

        # 读取并解析 schema 文件
        with open(self.schema_path, encoding='utf-8') as f:
            code = f.read().encode('utf-8')

        tree = self.parser.parse(code)

        # 遍历所有 prim_definition
        for child in tree.root_node.children:
            if child.type == 'prim_definition':
                class_info = self._parse_prim_definition(child)
                if class_info and class_info['name'].lower() != 'global':
                    self.classes_info[class_info['name']] = class_info
                    self.class_names.append(class_info['name'])

        self._parsed = True

    @staticmethod
    def _write_generated(file_path: str, content: str) -> None:
        """Write a generated file in the shape the linter expects.

        Schema docstrings carry the indentation of the source schema, so the raw
        text arrives with stray tabs and trailing blanks that ruff then reports as
        E101 and W291/W293 across every generated file. Normalising once here keeps
        regeneration from reintroducing them.
        """
        lines = content.replace('\t', '    ').expandtabs(4).splitlines()
        normalized = "\n".join(line.rstrip() for line in lines).rstrip() + "\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(normalized)

    def generate_pyclasses(self) -> None:
        """生成所有 Python 类文件（.py）

        如果尚未解析，会自动调用 parse() 方法。
        只为每个类生成对应的 .py 文件。
        """
        # 如果没有解析过，自动调用 parse
        if not self._parsed:
            self.parse()

        # 为每个类生成 Python 文件
        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            self._generate_class_file(class_name, class_info)

    def generate_pyi(self) -> None:
        """生成所有类型存根文件（.pyi）

        包括主类的 .pyi 文件和命名空间类的 .pyi 文件。
        必须在 generate_pyclasses 之后调用。
        """
        # 如果没有解析过，自动调用 parse
        if not self._parsed:
            self.parse()

        # 第一步：收集所有命名空间的成员
        namespace_members = self._collect_all_namespace_members()

        # A namespace prefix and a schema class can normalise to the same file
        # name (``lightList`` and ``LightList`` both become light_list.pyi). The
        # class stub is the one that is actually importable, so the namespace
        # members are merged into it instead of being written over it.
        class_stub_names = {self._camel_to_snake(name) + '.pyi' for name in self.class_names}

        # 第二步：为每个命名空间生成 .pyi 文件
        for ns_prefix, members in namespace_members.items():
            if not members:
                # An empty namespace class is not valid Python -- a class body has to
                # hold something -- and there is nothing to declare either, so the
                # file is not written at all.
                continue
            ns_class_name = self._snake_to_pascal(ns_prefix)
            ns_file_name = self._camel_to_snake(ns_prefix) + '.pyi'
            ns_file_path = os.path.join(self.schema_dir, ns_file_name)

            if ns_file_name in class_stub_names:
                print(f"Skipped namespace {ns_prefix}: collides with {ns_file_name}")
                continue

            # 生成命名空间类的 .pyi 文件
            ns_content = self._generate_namespace_pyi(ns_prefix, ns_class_name, members)
            if not ns_content:
                print(f"Skipped namespace {ns_prefix}: nothing declarable")
                continue
            self._write_generated(ns_file_path, ns_content)
            print(f"Generated namespace: {ns_file_path}")
            self._generated_ns_files.add(ns_prefix)

        # 第三步：重新生成所有类的 .pyi 文件（使用已生成的命名空间文件）
        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            base_class = self._determine_base_class(class_info)
            _, imported_token_classes = self._generate_token_classes(class_info['attributes'])
            self._regenerate_pyi_file(class_name, class_info, base_class, imported_token_classes)


    def generate_all(self) -> None:
        """生成所有文件（.py、.pyi 和 __init__.py）

        这是完整的生成流程，依次调用 generate_pyclasses、generate_pyi 和 generate_init_file。
        """
        self.generate_pyclasses()
        self.generate_pyi()
        self.generate_init_file()
        self.generate_puml()
        self.generate_api_accessors()

    def generate_api_accessors(self) -> None:
        """Write the API schema accessors into the hand-written pyusd/prim.py.

        These declarations used to be generated into pyusd/prim.pyi. A module that
        ships both a ``.py`` and a ``.pyi`` hands ``ty`` two unrelated ``Prim`` types,
        so every module annotating a ``Prim`` parameter then reported
        ``invalid-argument-type``; ``prim.pyi`` was the only stub left doing that.
        The declarations therefore move into ``prim.py``, which is the one module in
        the package that is hand-written and still receives generated members. That is
        why the region is fenced by markers and a missing marker raises instead of
        silently generating nothing.

        Each accessor is a typed forwarder onto ``PrimSpec.__getattr__``, which stays
        the single runtime path: the schema registry decides the return type, and
        ``Prim.__getattr__`` remains the fallback for a schema that appears without a
        regeneration. The bodies annotate a local rather than calling ``cast``, so the
        API classes are only needed at type-check time and the generated imports can
        stay inside ``TYPE_CHECKING``.

        One instance handles one schema directory, and ``generate_code.py`` builds a
        fresh instance per directory, so the regions merge rather than overwrite: the
        last directory parsed would otherwise be the only one represented.
        """
        if not self._parsed:
            self.parse()

        prim_module = self._find_root_prim_module()
        if prim_module is None:
            raise FileNotFoundError("Unable to find prim.py from schema directory")

        with open(prim_module, encoding='utf-8') as f:
            content = f.read()

        accessors, imports = self._collect_api_accessors(prim_module)
        if not accessors and not imports:
            return

        content = self._merge_fenced_region(
            content, 'generated api imports', imports,
            lambda key: key in content)

        # The accessors are declarations with no body, so they only need to exist for a
        # type checker. Wrapping the region in `if TYPE_CHECKING:` is what keeps the
        # runtime unimplemented: the class then has no such attributes, and Prim.__getattr__
        # stays the single path that resolves them. The imports they annotate already live
        # under the module-level TYPE_CHECKING block above the class.
        content = self._merge_fenced_region(
            content, 'generated api accessors', accessors,
            lambda key: re.search(rf"def {re.escape(key)}\(", content) is not None,
            fence_open='    if TYPE_CHECKING:',
            fence_close='')

        self._write_generated(prim_module, content)
        self._generate_target_api_accessors(prim_module)

    def _merge_fenced_region(
            self, content: str, name: str, items: List[Tuple[str, str]],
            present: Callable[[str], bool], fence_open: str = "", fence_close: str = "",
        ) -> str:
            """Add items to a marker-fenced region, skipping the ones already present.

            ``present`` decides whether an item is already declared. It cannot be a
            substring test on the file: an accessor named ``light_api`` is a substring of
            its own import line, ``from .lux.light_api import LightAPI``, so every
            accessor would look present the moment its import lands.

            Presence is judged against the whole file rather than the region, because
            ``ruff`` re-sorts import blocks and will carry the opening marker along with
            the imports it considers to belong before it, which would otherwise make a
            second generator run re-add those imports.

            The markers live in a hand-written file, so losing one has to be loud: a
            silent no-op would leave the accessors undeclared with no indication why.

            ``fence_open`` and ``fence_close`` wrap whatever is already inside the region
            as well as what is being added, which is how the accessor region ends up under
            ``if TYPE_CHECKING:`` without the generator having to know whether a previous
            run wrote forwarders or declarations there.
            """
            begin = f"    # --- BEGIN {name} ---"
            end = f"    # --- END {name} ---"
            lines = content.splitlines()
            try:
                first = lines.index(begin)
                last = lines.index(end)
            except ValueError:
                raise FileNotFoundError(
                    f"Missing '{begin.strip()}' / '{end.strip()}' marker pair; refusing "
                    f"to generate silently."
                ) from None
            if last < first:
                raise ValueError(f"Marker '{end.strip()}' precedes '{begin.strip()}'")

            existing = [line for line in lines[first + 1:last] if line.strip()]
            pending = [text for key, text in items if not present(key)]
            if not pending:
                return content

            # Strip a fence left by a previous run so regenerating cannot nest one.
            while existing and existing[0].strip() == fence_open.strip():
                existing.pop(0)
            while existing and existing[-1].strip() == fence_close.strip():
                existing.pop()

            # Ordering is left to ruff, which is the only thing that can sort the block
            # correctly: the hand-written imports sharing this block are not ours to move.
            body = existing + pending
            if fence_open:
                body = [fence_open] + body
            if fence_close:
                body = body + [fence_close]

            return "\n".join(lines[:first + 1] + body + lines[last:])

    def _find_root_prim_module(self) -> Optional[str]:
        """Locate the package-root prim.py by walking up from the schema directory.

        The walk starts at the schema directory itself rather than its parent: the
        core schema lives in the package root, next to prim.py, so the core API
        schemas would otherwise never find it.
        """
        current_dir = os.path.abspath(self.schema_dir)
        while current_dir and current_dir != os.path.dirname(current_dir):
            candidate = os.path.join(current_dir, 'prim.py')
            if os.path.isfile(candidate):
                return candidate
            current_dir = os.path.dirname(current_dir)
        return None

    def _is_api_schema_info(self, class_name: str, class_info: Dict[str, Any]) -> bool:
        if class_name == 'APISchemaBase':
            return False
        inherits = {
            parent.lstrip('</').rstrip('>')
            for parent in class_info.get('inherits', [])
        }
        if 'APISchemaBase' in inherits:
            return True
        api_schema_type = class_info.get('custom_data', {}).get('apiSchemaType', '')
        if api_schema_type in {
            'nonApplied',
            'nonAppliedAPI',
            'singleApply',
            'singleApplyAPI',
            'multipleApply',
            'multipleApplyAPI',
        }:
            return True
        return (
            class_info.get('kind') == 'class'
            and not class_info.get('has_explicit_name')
            and class_name.endswith('API')
        )

    def _generate_target_api_accessors(self, prim_module: str) -> None:
        """Declare the API accessors that are scoped to one prim type.

        ``apiSchemaCanOnlyApplyTo`` keeps these off ``Prim``: a ``Mesh`` has no
        ``material_x_config_api``. They go into the target class's generated stub
        instead, which is what the accessor has always done; dropping the routing
        would leave a full regeneration silently deleting them from the stub.
        """
        updates: Dict[str, List[Tuple[str, str, str]]] = {}
        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            if not self._is_api_schema_info(class_name, class_info):
                continue
            method_name = self._camel_to_snake(class_name)
            for target in self._get_api_schema_apply_targets(class_info):
                target_pyi = self._find_schema_stub_for_class(target, prim_module)
                if target_pyi is None:
                    raise FileNotFoundError(
                        f"No generated stub found for {target}, the only prim type "
                        f"{class_name} applies to."
                    )
                updates.setdefault(target_pyi, []).append(
                    (method_name, class_name,
                     self._api_import_statement(target_pyi, class_name)))

        for target_pyi, accessors in updates.items():
            self._add_accessors_to_stub(target_pyi, accessors)

    def _api_import_statement(self, target_pyi: str, class_name: str) -> str:
        """Import an API schema class relative to the stub that will declare it.

        The target stub is not necessarily in this generator's schema directory: a
        MaterialXConfigAPI accessor is declared on the shade Material stub, while the
        schema is parsed from mtlx. A ``pyusd.``-absolute import only resolves when the
        module happens to sit at the package root, which is false for every namespaced
        schema, so the path is derived from the two file locations instead.
        """
        module_name = self._camel_to_snake(class_name)
        schema_dir = os.path.abspath(self.schema_dir)
        relative = os.path.relpath(schema_dir, os.path.dirname(os.path.abspath(target_pyi)))
        prefix = '.' if relative == '.' else '.' + relative.replace(os.sep, '.')
        return f"from {prefix}{module_name} import {class_name}"

    def _find_schema_stub_for_class(
        self, class_name: str, prim_module: str
    ) -> Optional[str]:
        """Find the generated stub that declares a schema class, if there is one."""
        search_names = self._schema_class_name_candidates(class_name)
        search_dirs = [
            os.path.abspath(self.schema_dir),
            os.path.dirname(os.path.abspath(prim_module)),
        ]
        for search_dir in search_dirs:
            for candidate_name in search_names:
                candidate = os.path.join(
                    search_dir, self._camel_to_snake(candidate_name) + '.pyi')
                if os.path.isfile(candidate):
                    return candidate

        root_dir = os.path.dirname(os.path.abspath(prim_module))
        for current_dir, dir_names, file_names in os.walk(root_dir):
            dir_names[:] = [name for name in dir_names if name != '__pycache__']
            for candidate_name in search_names:
                file_name = self._camel_to_snake(candidate_name) + '.pyi'
                if file_name in file_names:
                    return os.path.join(current_dir, file_name)
        return None

    def _schema_class_name_candidates(self, class_name: str) -> List[str]:
        candidates = [class_name]
        for known_class_name in self.class_names:
            if class_name.endswith(known_class_name) and known_class_name not in candidates:
                candidates.append(known_class_name)
        if class_name.startswith('Usd') and len(class_name) > 3:
            stripped = class_name[3:]
            for known_class_name in self.class_names:
                if stripped.endswith(known_class_name) and known_class_name not in candidates:
                    candidates.append(known_class_name)
        return candidates

    def _add_accessors_to_stub(
        self, stub_path: str, accessors: List[Tuple[str, str, str]]
    ) -> None:
        """Append the accessors to a fully generated stub, skipping known ones.

        The stub is generated from top to bottom and its class body reaches end of
        file, which is what makes appending land inside the class. Appending rather
        than rewriting also keeps a re-run from reordering what is already there.
        """
        with open(stub_path, encoding='utf-8') as f:
            content = f.read()

        missing: List[str] = []
        for method_name, class_name, import_stmt in accessors:
            content = self._ensure_import(content, import_stmt, class_name)
            if re.search(rf"def {re.escape(method_name)}\(", content):
                continue
            missing.append(self._format_stub_api_accessor(method_name, class_name))

        if missing:
            content = content.rstrip() + "\n\n" + "\n\n".join(missing) + "\n"

        self._write_generated(stub_path, content)

    def _ensure_import(
        self, content: str, import_stmt: str, class_name: str
    ) -> str:
        """Make sure the stub imports the class from the path the accessor needs.

        Matching is done on the parsed statement rather than on its text: the
        generated stubs wrap long imports in parentheses across several lines, so a
        textual test misses an import that is already there and appends a duplicate.
        Comparing the unparsed form also catches a same-named import from the wrong
        path, which is how a ``pyusd.``-absolute statement pointing at a namespaced
        module survived here in the first place.
        """
        wanted = ast.unparse(ast.parse(import_stmt).body[0])
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return self._insert_imports(content, [import_stmt])

        for node in tree.body:
            if not isinstance(node, ast.ImportFrom):
                continue
            if not any(alias.name == class_name for alias in node.names):
                continue
            if ast.unparse(node) == wanted:
                return content
            lines = content.splitlines()
            return "\n".join(lines[:node.lineno - 1] + [import_stmt]
                             + lines[node.end_lineno:]) + (
                                 '\n' if content.endswith('\n') else '')

        return self._insert_imports(content, [import_stmt])

    def _format_stub_api_accessor(self, method_name: str, class_name: str) -> str:
        return "\n".join([
            "    @property",
            f"    def {method_name}(self)->{class_name}: ...",
        ])


    def _insert_imports(self, content: str, import_statements: List[str]) -> str:
        """Insert statements after the stub's import block, not after its first line.

        The generated stubs wrap long imports in parentheses across several lines, so
        looking for the last line that starts with ``from `` lands on the opening line
        and injects the new statement into the middle of the parenthesised list.
        """
        unique_imports: List[str] = []
        for import_stmt in import_statements:
            if import_stmt not in unique_imports and import_stmt not in content:
                unique_imports.append(import_stmt)
        if not unique_imports:
            return content

        lines = content.splitlines()
        end = 0
        in_import = False
        for index, line in enumerate(lines):
            stripped = line.strip()
            if line.startswith(('from ', 'import ')):
                in_import = True
                end = index + 1
            elif in_import and (not stripped
                                or line.startswith((' ', '\t'))
                                or stripped.startswith((')', ']', ','))):
                end = index + 1
            else:
                break

        lines[end:end] = unique_imports
        line_ending = '\n' if content.endswith('\n') else ''
        return '\n'.join(lines) + line_ending

    def _collect_api_accessors(
        self, prim_module: str
    ) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """Build the accessor blocks and the imports they need.

        Only accessors open on ``Prim`` are collected here. The ones scoped by
        ``apiSchemaCanOnlyApplyTo`` are handled by ``_generate_target_api_accessors``.
        """
        accessors: List[Tuple[str, str]] = []
        imports: List[Tuple[str, str]] = []
        seen = set()
        prim_dir = os.path.dirname(os.path.abspath(prim_module))
        rel_dir = os.path.relpath(os.path.abspath(self.schema_dir), prim_dir)
        prefix = [] if rel_dir == '.' else rel_dir.split(os.sep)

        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            if not self._is_api_schema_info(class_name, class_info):
                continue
            if self._get_api_schema_apply_targets(class_info):
                continue

            method_name = self._camel_to_snake(class_name)
            if method_name in seen:
                continue
            seen.add(method_name)

            statement = f"from {'.'.join([''] + prefix + [method_name])} import {class_name}"
            imports.append((statement, f"    {statement}"))
            accessors.append((method_name, self._format_api_accessor(
                method_name, class_name, self._determine_schema_kind(class_info))))

        return accessors, imports

    def _get_api_schema_apply_targets(self, class_info: Dict[str, Any]) -> List[str]:
        custom_data = class_info.get('custom_data', {})
        targets = custom_data.get('apiSchemaCanOnlyApplyTo')
        if isinstance(targets, str):
            return [targets]
        if isinstance(targets, list):
            return [target for target in targets if isinstance(target, str)]
        return []

    def _format_api_accessor(
        self, method_name: str, class_name: str, schema_kind: str
    ) -> str:
        """A declaration for one API schema, with no body.

        These are declarations rather than forwarders. Prim.__getattr__ already routes
        every ``*_api`` name to PrimSpec.__getattr__, which consults the registry and
        returns the schema object or an APIWrapper, so a generated body would be a second
        implementation of a path that already exists -- 41 of them, each three lines.

        They live under ``if TYPE_CHECKING`` so the class carries them for a type checker
        and an IDE while the runtime never sees them and attribute access keeps falling
        through to Prim.__getattr__. That placement is what makes this possible without a
        stub: a module must not ship both a .py and a .pyi, because ty then treats the two
        declarations of the same class as distinct nominal types. A pyusd/prim.pyi holding
        these was measured at needing the whole public surface of Prim re-declared -- 68
        members -- to keep importers seeing anything at all, and still left six
        dual-identity errors in prim.py to be suppressed.

        MultipleApplyAPI schemas take an instance name; the rest are single-apply and read
        as properties, which is how the generated accessors in the schema stubs spell them.
        """
        if schema_kind == 'SchemaKind.MultipleApplyAPI':
            return "\n".join([
                "        def " + method_name + "(self, instance_name:str)->" + class_name + ": ...",
            ])
        return "\n".join([
            "        @property",
            "        def " + method_name + "(self)->" + class_name + ": ...",
        ])
        return "\n".join([
            "    @property",
            f"    def {method_name}(self)->{class_name}:",
            f'        api:Any = getattr(self._edit_spec(), "{method_name}")',
            f"        result:{class_name} = api",
            "        return result",
        ])

    def generate_puml(self, output_file: Optional[str] = None) -> None:
        """生成 PlantUML 格式的类图

        Args:
            output_file: 输出文件路径，默认为 schema_dir 下的 classes.puml
        """
        if not self._parsed:
            self.parse()

        if output_file is None:
            output_file = os.path.join(self.schema_dir, 'classes.puml')

        lines = []
        lines.append("@startuml")
        lines.append(f"' {os.path.basename(self.schema_dir)} Classes Inheritance and Properties Diagram")
        lines.append("")

        # 按继承层级分组类
        abstract_classes = []
        concrete_classes = []

        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            kind = class_info.get('kind', '')
            has_explicit_name = class_info.get('has_explicit_name', False)

            # AbstractTyped 或 APISchemaBase 的子类视为抽象类
            if kind == 'class' and not has_explicit_name:
                abstract_classes.append(class_info)
            else:
                concrete_classes.append(class_info)

        # 生成抽象类定义
        if abstract_classes:
            lines.append("' Abstract base classes")
            for class_info in abstract_classes:
                lines.extend(self._generate_puml_class(class_info))
                lines.append("")

        # 生成具体类定义
        if concrete_classes:
            lines.append("' Concrete classes")
            for class_info in concrete_classes:
                lines.extend(self._generate_puml_class(class_info))
                lines.append("")

        # 生成继承关系
        lines.append("' Relationships")
        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            inherits = class_info.get('inherits', [])

            for parent in inherits:
                # 只包含当前模块中的父类
                parent_name = parent.lstrip('</').rstrip('>')
                if parent_name in self.classes_info:
                    lines.append(f"{parent_name} <|-- {class_name}")

        lines.append("")
        lines.append("@enduml")

        # 写入文件
        self._write_generated(output_file, "\n".join(lines) + "\n")

        print(f"Generated PlantUML: {output_file}")

    def _generate_puml_class(self, class_info: Dict[str, Any]) -> List[str]:
        """生成单个类的 PlantUML 定义"""
        lines = []
        class_name = class_info['name']

        lines.append(f"class {class_name} {{")

        # 添加属性
        for attr in class_info['attributes']:
            attr_name = attr.get('full_name', attr['name'])
            attr_type = self._usd_type_to_python_type(attr['type'])

            # 处理 allowedTokens
            if attr.get('allowed_tokens'):
                attr_type = self._snake_to_pascal(attr['name'])

            # 构建属性字符串
            attr_str = f"    +{attr_name}: {attr_type}"

            # 添加默认值
            default_value = attr.get('default')
            if default_value is not None:
                py_default = self._format_puml_default(default_value, attr['type'])
                attr_str += f" = {py_default}"

            lines.append(attr_str)

        # 添加关系
        for rel in class_info['relationships']:
            rel_name = rel.get('full_name', rel['name'])
            lines.append(f"    +{rel_name}: RelationshipSpec")

        lines.append("}")

        return lines

    def _format_puml_default(self, value: Any, usd_type: str) -> str:
        """格式化 PlantUML 中的默认值"""
        if isinstance(value, bool):
            return str(value).lower()  # true/false
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                return "[]"
            # 格式化列表元素
            elements = [self._format_puml_default(v, usd_type.replace('[]', '')) for v in value]
            return f"[{', '.join(elements)}]"
        elif isinstance(value, dict):
            # 简单字典格式化
            items = [f"{k}: {self._format_puml_default(v, '')}" for k, v in value.items()]
            return "{" + ", ".join(items) + "}"
        else:
            return str(value)

    @staticmethod
    @beartype
    def generate_schema(module: ModuleType)->None:
        from .api_schema_base import APISchemaBase
        from .typed import Typed

        result_list = []
        for cls_name in module.__all__:
            cls = getattr(module, cls_name)
            if isinstance(cls, type) and issubclass(cls, (Typed, APISchemaBase)):
                result_list.append(cls.cls_to_str())

        result = "\n".join(result_list)
        target_file_path = os.path.join(os.path.dirname(module.__file__ or ""), "schema_generated.usda")
        CodeGenerator._write_generated(target_file_path, result)


    def _collect_all_namespace_members(self) -> Dict[str, List[Dict[str, Any]]]:
        """收集所有类的命名空间成员"""
        namespace_members = {}

        for class_info in self.classes_info.values():
            # 收集属性
            for attr in class_info['attributes']:
                full_name = attr.get('full_name', attr['name'])
                if ':' in full_name:
                    ns_prefix = full_name.split(':')[0]
                    if ns_prefix not in namespace_members:
                        namespace_members[ns_prefix] = []
                    # 避免重复添加（使用 full_name 作为唯一标识）
                    if not any(m.get('full_name') == full_name for m in namespace_members[ns_prefix]):
                        namespace_members[ns_prefix].append(attr)

            # 收集关系
            for rel in class_info['relationships']:
                full_name = rel.get('full_name', rel['name'])
                if ':' in full_name:
                    ns_prefix = full_name.split(':')[0]
                    if ns_prefix not in namespace_members:
                        namespace_members[ns_prefix] = []
                    # 避免重复添加（使用 full_name 作为唯一标识）
                    if not any(m.get('full_name') == full_name for m in namespace_members[ns_prefix]):
                        namespace_members[ns_prefix].append(rel)

        return namespace_members

    def _regenerate_pyi_file(self, class_name: str, class_info: Dict[str, Any], base_class: str, imported_token_classes: List[str]) -> None:
        """重新生成 .pyi 文件（使用已生成的命名空间文件）"""
        # 生成主类的导入语句（不包含 SchemaKind）
        pyi_imports = self._generate_pyi_imports(base_class, class_info, imported_token_classes, self._generated_ns_files)

        # 生成类定义（只有签名，没有实现）
        pyi_class_def = self._generate_pyi_class_definition(class_name, base_class, class_info, self._generated_ns_files)

        # 组合内容
        content = pyi_imports + "\n\n" + pyi_class_def + "\n"

        # 写入 .pyi 文件
        file_name = self._camel_to_snake(class_name) + '.pyi'
        file_path = os.path.join(self.schema_dir, file_name)

        # A stub for a hand-written module is the hazard the class file guard exists
        # for, and worse: a module shipping both a .py and a .pyi hands ty two unrelated
        # classes, so every annotation that mentions one of them fails. The test is the
        # one already used on the .py path -- a stub cannot use "has a real body",
        # because 52 generated stubs carry property getters whose body is a docstring.
        module_path = os.path.join(
            self.schema_dir, self._camel_to_snake(class_name) + '.py')
        if self._holds_hand_written_code(module_path):
            print(f"Skipped {file_path}: hand-written module, no stub generated.")
            return

        self._write_generated(file_path, content)

    @staticmethod
    def _node_text(node: Node) -> str:
        """Decoded source text of a tree-sitter node.

        ``Node.text`` is typed as ``Optional[bytes]`` and is None only for
        zero-width or error nodes, which the schema walk never asks for.
        """
        text = node.text
        return "" if text is None else text.decode('utf-8')

    def _parse_prim_definition(self, node: Node) -> Dict[str, Any]:
        """解析 prim_definition 节点，提取类信息"""
        info = {
            'name': '',
            'kind': '',
            'has_explicit_name': False,
            'inherits': [],
            'doc': '',
            'custom_data': {},
            'metadata': {},
            'attributes': [],
            'relationships': [],
            'api_schemas': [],
        }

        for child in node.named_children:
            if child.type == 'prim_type':
                info['kind'] = self._node_text(child).strip()
            elif child.type == 'string':
                name = self._node_text(child).strip('"')
                info['name'] = name
                prev_sibling = child.prev_named_sibling
                if prev_sibling and prev_sibling.type == 'identifier':
                    info['has_explicit_name'] = True
            elif child.type == 'metadata':
                self._parse_metadata(child, info)
            elif child.type == 'block':
                self._parse_block(child, info)

        return info

    def _parse_metadata(self, node: Node, info: Dict[str, Any]) -> None:
        """解析元数据"""
        for child in node.named_children:
            if child.type == 'metadata_assignment':
                orderer = ''
                key = ''
                value = None
                value_dict = None
                value_path = None
                value_list = None
                for assign_child in child.named_children:
                    if assign_child.type == 'orderer':
                        orderer = self._node_text(assign_child)
                    elif assign_child.type == 'identifier':
                        key = self._node_text(assign_child)
                    elif assign_child.type == 'string':
                        text = self._node_text(assign_child)
                        # 处理三引号字符串
                        if text.startswith("'''") and text.endswith("'''") or text.startswith('"""') and text.endswith('"""'):
                            value = text[3:-3]
                        else:
                            value = text.strip('"')
                    elif assign_child.type == 'dictionary':
                        value_dict = self._parse_usd_dictionary(assign_child)
                    elif assign_child.type == 'arc_path':
                        value_path = self._node_text(assign_child)
                    elif assign_child.type == 'list':
                        value_list = self._parse_usd_list(assign_child)

                # 组合 orderer 和 key
                full_key = f"{orderer} {key}" if orderer else key

                if key == 'documentation' or key == 'doc':
                    info['doc'] = value or ''
                elif key == 'customData' and value_dict:
                    info['custom_data'] = value_dict
                    # 同时保存到 metadata
                    if not info.get('metadata'):
                        info['metadata'] = {}
                    info['metadata']['customData'] = value_dict
                elif key == 'inherits' and value_path:
                    # inherits 可以是单个路径或路径列表
                    info['inherits'].append(value_path)
                elif full_key == 'prepend apiSchemas' and value_list:
                    info['api_schemas'] = value_list
                    # 同时保存到 metadata，保留完整的 key
                    if not info.get('metadata'):
                        info['metadata'] = {}
                    info['metadata'][full_key] = value_list
                else:
                    # 其他所有字段都保存到 metadata
                    if value is not None or value_dict is not None or value_list is not None:
                        if not info.get('metadata'):
                            info['metadata'] = {}
                        if value_dict is not None:
                            info['metadata'][full_key] = value_dict
                        elif value_list is not None:
                            info['metadata'][full_key] = value_list
                        elif value is not None:
                            info['metadata'][full_key] = value
            elif child.type == 'attribute_assignment':
                self._parse_attribute_assignment(child, info)

    def _parse_attribute_assignment(self, node: Node, info: Dict[str, Any]) -> None:
        """解析属性赋值"""
        key = ''
        value = None

        for child in node.named_children:
            if child.type == 'identifier':
                key = self._node_text(child)
            elif child.type == 'string':
                value = self._node_text(child).strip('"')
            elif child.type == 'array':
                value = self._parse_usd_array(child)
            elif child.type == 'dictionary':
                value = self._parse_usd_dictionary(child)

        if key == 'apiSchemas' and isinstance(value, list):
            info['api_schemas'] = value

    def _parse_block(self, node: Node, info: Dict[str, Any]) -> None:
        """解析块内容（属性、关系等）"""
        for child in node.named_children:
            if child.type in ['attribute_declaration', 'attribute_assignment']:
                attr_info = self._parse_attribute_declaration(child)
                if attr_info:
                    info['attributes'].append(attr_info)
            elif child.type == 'relationship_declaration':
                rel_info = self._parse_relationship_declaration(child)
                if rel_info:
                    info['relationships'].append(rel_info)
            elif child.type == 'metadata_assignment':
                self._parse_custom_data_assignment(child, info)

    def _parse_custom_data_assignment(self, node: Node, info: Dict[str, Any]) -> None:
        """解析 customData 赋值"""
        key = ''
        for child in node.named_children:
            if child.type == 'identifier':
                key = self._node_text(child)
            elif child.type == 'dictionary' and key == 'customData':
                info['custom_data'] = self._parse_usd_dictionary(child)
                # 同时保存到 metadata
                if info['custom_data']:
                    info['metadata']['customData'] = info['custom_data']

    def _parse_attribute_declaration(self, node: Node) -> Dict[str, Any]:
        """解析属性声明"""
        attr_info = {
            'name': '',
            'full_name': '',
            'type': '',
            'is_uniform': False,
            'default_value': None,
            'doc': '',
            'allowed_tokens': [],
            'api_name': '',
            'metadata': {},
        }

        # Iterate node.children rather than node.named_children: the grammar puts no
        # wrapper around a default value, so the only way to find one is to notice the
        # `=` and take the sibling after it. `=` is anonymous, so it is absent from
        # named_children.
        children = node.children
        for index, child in enumerate(children):
            if child.type == 'attribute_type':
                attr_info['type'] = self._node_text(child)
            elif child.type == 'identifier' or child.type == 'qualified_identifier':
                # qualified_identifier 包含 namespace:name 格式
                full_name = self._node_text(child)
                attr_info['full_name'] = full_name
                # 如果有冒号，提取最后一部分作为 Python 属性名
                if ':' in full_name:
                    attr_info['name'] = full_name.split(':')[-1]
                else:
                    attr_info['name'] = full_name
            elif child.type == 'uniform':
                attr_info['is_uniform'] = True
            elif child.type == '=':
                if index + 1 < len(children):
                    attr_info['default_value'] = self._parse_default_value(
                        children[index + 1]
                    )
            elif child.type == 'metadata':
                self._parse_attribute_metadata(child, attr_info)
        return attr_info

    def _literal_value(self, node: Node) -> Tuple[bool, Any]:
        """Convert one literal node to Python; False when it is not a literal."""
        kind = node.type
        text = self._node_text(node)
        if kind == 'string':
            return True, text.strip('"')
        if kind == 'bool':
            return True, text == 'true'
        if kind in ('int', 'integer'):
            # The grammar spells it `integer`; the old code only looked for `int`.
            return True, int(text)
        if kind == 'identifier':
            # A bare token value, as in `token t = foo`.
            return True, text
        if kind == 'float':
            if text == 'inf':
                return True, float('inf')
            if text == '-inf':
                return True, float('-inf')
            return True, float(text)
        if kind in ('list', 'array'):
            return True, self._parse_usd_array(node)
        if kind == 'tuple':
            # A vector default, as in `quatf physics:localRot0 = (1.0, 0.0, 0.0, 0.0)`.
            # Handling it here rather than letting the caller's fallback descend into
            # the tuple is what stops the first component being taken as the default
            # for the whole attribute.
            numbers = []
            for part in node.named_children:
                ok, number = self._literal_value(part)
                numbers.append(number if ok else self._node_text(part))
            return True, tuple(numbers)
        if kind == 'dictionary':
            return True, self._parse_usd_dictionary(node)
        return False, None

    def _parse_default_value(self, node: Node) -> Any:
        """解析默认值

        tree-sitter-usd 没有 default_value 这种节点。声明 `double radius = 1.0` 解析出来是
        attribute_assignment 底下的 attribute_type / identifier / = / float，默认值就是
        `=` 之后那个字面量节点本身。以前这里只在子节点里找 default_value，于是这个分支
        永远不成立，全部 347 个属性一个默认值都没解析出来，生成的结果因此丢掉了默认
        value。两种形态都接受：既支持字面量节点本身，也支持包着字面量的容器节点。
        """
        matched, value = self._literal_value(node)
        if matched:
            return value

        for child in node.named_children:
            matched, value = self._literal_value(child)
            if matched:
                return value

        return None

    def _parse_attribute_metadata(self, node: Node, attr_info: Dict[str, Any]) -> None:
        """解析属性元数据"""
        for child in node.named_children:
            if child.type == 'metadata_assignment':
                key = ''
                for assign_child in child.named_children:
                    if assign_child.type == 'identifier':
                        key = self._node_text(assign_child)
                    elif assign_child.type == 'string' and key == 'doc':
                        attr_info['doc'] = self._node_text(assign_child).strip('"')
                    elif (assign_child.type == 'array' or assign_child.type == 'list') and key == 'allowedTokens':
                        for item in assign_child.named_children:
                            if item.type == 'string':
                                attr_info['allowed_tokens'].append(self._node_text(item).strip('"'))
                    elif assign_child.type == 'dictionary' and key == 'customData':
                        custom_data = self._parse_usd_dictionary(assign_child)
                        if 'apiName' in custom_data:
                            attr_info['api_name'] = custom_data['apiName']
                        if custom_data:
                            attr_info['metadata']['customData'] = custom_data
                    elif key not in ['doc', 'allowedTokens']:
                        value = None
                        if assign_child.type == 'string':
                            value = self._node_text(assign_child).strip('"')
                        elif assign_child.type == 'bool':
                            value = self._node_text(assign_child) == 'true'
                        elif assign_child.type == 'int':
                            value = int(self._node_text(assign_child))
                        elif assign_child.type == 'float':
                            value = float(self._node_text(assign_child))
                        elif assign_child.type == 'array':
                            value = self._parse_usd_array(assign_child)
                        elif assign_child.type == 'dictionary':
                            value = self._parse_usd_dictionary(assign_child)

                        if value is not None:
                            attr_info['metadata'][key] = value

    def _parse_relationship_declaration(self, node: Node) -> Dict[str, Any]:
        """解析关系声明"""
        rel_info = {
            'name': '',
            'full_name': '',
            'doc': '',
            'api_name': '',
            'metadata': {},
        }

        for child in node.named_children:
            if child.type == 'identifier' or child.type == 'qualified_identifier':
                full_name = self._node_text(child)
                rel_info['full_name'] = full_name
                # 如果有冒号，提取最后一部分作为 Python 关系名
                if ':' in full_name:
                    rel_info['name'] = full_name.split(':')[-1]
                else:
                    rel_info['name'] = full_name
            elif child.type == 'metadata':
                self._parse_relationship_metadata(child, rel_info)

        return rel_info

    def _parse_relationship_metadata(self, node: Node, rel_info: Dict[str, Any]) -> None:
        """解析关系元数据"""
        for child in node.named_children:
            if child.type == 'metadata_assignment':
                key = ''
                for assign_child in child.named_children:
                    if assign_child.type == 'identifier':
                        key = self._node_text(assign_child)
                    elif assign_child.type == 'string' and key == 'doc':
                        rel_info['doc'] = self._node_text(assign_child).strip('"')
                    elif assign_child.type == 'dictionary' and key == 'customData':
                        custom_data = self._parse_usd_dictionary(assign_child)
                        if 'apiName' in custom_data:
                            rel_info['api_name'] = custom_data['apiName']
                        if custom_data:
                            rel_info['metadata']['customData'] = custom_data
                    elif key != 'doc':
                        value = None
                        if assign_child.type == 'string':
                            value = self._node_text(assign_child).strip('"')
                        elif assign_child.type == 'bool':
                            value = self._node_text(assign_child) == 'true'
                        elif assign_child.type == 'int':
                            value = int(self._node_text(assign_child))
                        elif assign_child.type == 'float':
                            value = float(self._node_text(assign_child))
                        elif assign_child.type == 'array':
                            value = self._parse_usd_array(assign_child)
                        elif assign_child.type == 'dictionary':
                            value = self._parse_usd_dictionary(assign_child)

                        if value is not None:
                            rel_info['metadata'][key] = value

    def _parse_usd_array(self, node: Node) -> List[Any]:
        """解析 USD 数组"""
        result = []
        for child in node.named_children:
            matched, value = self._literal_value(child)
            if matched:
                result.append(value)
            else:
                result.append(self._node_text(child))
        return result

    def _parse_usd_list(self, node: Node) -> List[Any]:
        """解析 USD 列表（与 array 类似）"""
        return self._parse_usd_array(node)

    def _parse_usd_dictionary(self, node: Node) -> Dict[str, Any]:
        """解析 USD 格式的字典"""
        result = {}

        for child in node.named_children:
            if child.type == 'dictionary_item':
                key = ''
                value = None
                for item_child in child.named_children:
                    if item_child.type == 'identifier':
                        key = self._node_text(item_child)
                    elif item_child.type == 'string':
                        text = self._node_text(item_child)
                        # 处理三引号字符串
                        if text.startswith("'''") and text.endswith("'''") or text.startswith('"""') and text.endswith('"""'):
                            value = text[3:-3]
                        else:
                            value = text.strip('"')
                    elif item_child.type == 'bool':
                        value = self._node_text(item_child) == 'true'
                    elif item_child.type == 'int':
                        value = int(self._node_text(item_child))
                    elif item_child.type == 'float':
                        text = self._node_text(item_child)
                        if text == 'inf':
                            value = float('inf')
                        elif text == '-inf':
                            value = float('-inf')
                        else:
                            value = float(text)
                    elif item_child.type == 'array':
                        value = self._parse_usd_array(item_child)
                    elif item_child.type == 'dictionary':
                        value = self._parse_usd_dictionary(item_child)

                if key:
                    result[key] = value
            elif child.type == 'attribute_type':
                self._node_text(child)
                key = ''
                value = None

                next_sibling = child.next_named_sibling
                while next_sibling:
                    if next_sibling.type == 'identifier' and not key:
                        key = self._node_text(next_sibling)
                    elif next_sibling.type == 'string' and key and value is None:
                        text = self._node_text(next_sibling)
                        # 处理三引号字符串
                        if text.startswith("'''") and text.endswith("'''") or text.startswith('"""') and text.endswith('"""'):
                            value = text[3:-3]
                        else:
                            value = text.strip('"')
                        break
                    elif next_sibling.type == 'bool' and key and value is None:
                        value = self._node_text(next_sibling) == 'true'
                        break
                    elif next_sibling.type == 'int' and key and value is None:
                        value = int(self._node_text(next_sibling))
                        break
                    elif next_sibling.type == 'float' and key and value is None:
                        text = self._node_text(next_sibling)
                        if text == 'inf':
                            value = float('inf')
                        elif text == '-inf':
                            value = float('-inf')
                        else:
                            value = float(text)
                        break
                    elif next_sibling.type == 'array' and key and value is None:
                        value = self._parse_usd_array(next_sibling)
                        break
                    elif next_sibling.type == 'list' and key and value is None:
                        value = self._parse_usd_list(next_sibling)
                        break
                    elif next_sibling.type == 'dictionary' and key and value is None:
                        value = self._parse_usd_dictionary(next_sibling)
                        break

                    next_sibling = next_sibling.next_named_sibling

                if key:
                    result[key] = value

        return result

    def _determine_base_class(self, class_info: Dict[str, Any]) -> str:
        """确定基类

        ``inherits`` is the only thing consulted. It used to be preceded by a shortcut
        returning ``APISchemaBase`` for any ``class`` without an explicit name, which
        caught every schema pulled in from an ``#include`` rather than declared in the
        .usda itself: ``Imageable``, ``Xformable``, ``Boundable`` and ``Gprim`` all
        lost their real parent and regenerated as ``APISchemaBase``. The shortcut is
        redundant anyway, because an API schema's parent *is* ``APISchemaBase``.
        """
        # 优先使用 inherits 字段
        inherits = class_info.get('inherits', [])
        if inherits:
            parent_name = inherits[0]
            # 去除路径格式 </...>
            parent_name = parent_name.lstrip('</').rstrip('>')

            # 特殊处理已知基类
            base_class_mapping = {
                'Typed': 'Typed',
                'APISchemaBase': 'APISchemaBase',
                'Imageable': 'Imageable',
                'Xformable': 'Xformable',
                'Boundable': 'Boundable',
                'Gprim': 'Gprim',
                'PointBased': 'PointBased',
                'GeomSubset': 'GeomSubset',
            }

            if parent_name in base_class_mapping:
                return base_class_mapping[parent_name]

            # 如果父类是当前模块中的其他类，直接返回父类名
            if parent_name in self.classes_info:
                return parent_name

        # 无 inherits：只剩两个手写根类。Prim 是本项目里所有 schema 类的根，
        # 所以 Typed 的基类是 Prim 而不是它自己。
        return 'Prim'

    def _determine_schema_kind(self, class_info: Dict[str, Any]) -> str:
        """确定 schema_kind

        是否为 API schema 由父类或 ``apiSchemaType`` 决定，绝不能靠"没有显式名字"
        来判断。那个判断原本排在最前面，导致所有从 ``#include`` 引入（而非在 .usda 里
        直接声明）的 schema 都被当成 ``NonAppliedAPI``：``Xformable`` 会被重新生成为
        API schema，而它实际是 ``AbstractTyped``。``VisibilityAPI`` 完全没有
        ``apiSchemaType``，所以父类也必须参与判断，否则它会被误判为 typed schema。
        """
        inherits = class_info.get('inherits', [])
        parent = inherits[0].lstrip('</').rstrip('>') if inherits else ''
        api_schema_type = class_info.get('custom_data', {}).get('apiSchemaType', '')

        if parent == 'APISchemaBase' or api_schema_type:
            if api_schema_type in ('singleApply', 'singleApplyAPI'):
                return 'SchemaKind.SingleApplyAPI'
            if api_schema_type in ('multipleApply', 'multipleApplyAPI'):
                return 'SchemaKind.MultipleApplyAPI'
            return 'SchemaKind.NonAppliedAPI'

        # Typed schemas
        if class_info.get('has_explicit_name'):
            return 'SchemaKind.ConcreteTyped'

        return 'SchemaKind.AbstractTyped'

    def _generate_class_file(self, class_name: str, class_info: Dict[str, Any]) -> None:
        up = self._package_prefix()
        """生成单个类的 Python 文件（.py）"""
        base_class = self._determine_base_class(class_info)

        # 生成导入语句
        imports = self._generate_imports(base_class, class_info)

        # 检查是否有需要从 common.py 导入的枚举类
        token_classes, imported_token_classes = self._generate_token_classes(class_info['attributes'])
        if token_classes:
            imports += "\nfrom enum import ReprEnum"

        # A token[] with allowedTokens is declared List[SomeEnum], which _generate_imports
        # cannot see because it only looks at the schema's own type name. Collect it here
        # so the annotation resolves.
        if any(
            attr.get('allowed_tokens') and attr['type'].endswith('[]')
            for attr in class_info['attributes']
        ) and "from typing import List" not in imports:
            imports += "\nfrom typing import List"

        if imported_token_classes:
            imports += f"\nfrom {up}common import {', '.join(sorted(set(imported_token_classes)))}"

        # 生成类定义
        class_def = self._generate_class_definition(class_info)

        # 组合完整内容
        content = imports + "\n\n\n" + class_def + "\n"

        # 写入 .py 文件
        file_name = self._camel_to_snake(class_name) + '.py'
        file_path = os.path.join(self.schema_dir, file_name)

        if self._holds_hand_written_code(file_path):
            print(f"Skipped {file_path}: hand-written module, not regenerable. "
                  f"Edit it by hand; the generator will not overwrite it.")
            return

        self._write_generated(file_path, content)

        print(f"Generated: {file_path}")

    def _package_prefix(self) -> str:
        """Relative prefix that reaches the package root from this schema directory.

        Every generated module imports the shared core modules -- ``attribute``,
        ``common``, ``dtypes``, ``gf``, ``typed``, ``api_schema_base`` -- from the
        package root. That used to be spelled ``..`` everywhere, which is right for a
        namespace directory such as ``pyusd/geom`` but escapes the package when the
        schema *is* the root one: regenerating ``pyusd/typed.py`` produced
        ``from {up}common import SchemaKind``, which does not resolve.

        The package root is the directory holding this module, so the prefix is a
        plain relative path from the schema directory to it.
        """
        root = os.path.dirname(os.path.abspath(__file__))
        relative = os.path.relpath(root, os.path.abspath(self.schema_dir))
        return relative.replace(os.sep, '.')

    @staticmethod
    def _holds_hand_written_code(file_path: str) -> bool:
        """Whether an existing target file carries code the generator never emits.

        ``pyusd/api_schema_base.py`` and ``pyusd/model_api.py`` are written by hand but
        sit exactly where ``generate_pyclasses`` writes, so a full ``generate_all``
        used to replace them with a schema dump and lose their implementations. A
        generated class file only ever declares ``meta``, ``schema_kind`` and attribute
        values; every method body in one is ``...``. So a function with a real body is
        a reliable signal of a hand-owned module, and it needs no list that can go
        stale the moment somebody adds another hand-written file.

        A file that does not parse is not treated as hand-written: it is already
        broken, and refusing to regenerate it would only prevent its repair.
        """
        if not os.path.isfile(file_path):
            return False

        try:
            with open(file_path, encoding='utf-8') as handle:
                tree = ast.parse(handle.read())
        except (OSError, SyntaxError, ValueError):
            return False

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = [n for n in node.body if not isinstance(n, ast.Pass)]
            if not body:
                continue
            if len(body) == 1 and isinstance(body[0], ast.Expr):
                value = body[0].value
                if isinstance(value, ast.Constant) and value.value is Ellipsis:
                    continue
            return True
        return False

    def _generate_pyi_file(self, class_name: str, class_info: Dict[str, Any], base_class: str, imported_token_classes: List[str]) -> None:
        """生成类型存根文件 (.pyi) - 第一遍生成（不包含命名空间导入）"""
        # 生成主类的导入语句（不包含 SchemaKind 和命名空间导入）
        pyi_imports = self._generate_pyi_imports(base_class, class_info, imported_token_classes, set())

        # 生成类定义（只有签名，没有实现）
        pyi_class_def = self._generate_pyi_class_definition(class_name, base_class, class_info, set())

        # 组合内容
        content = pyi_imports + "\n\n" + pyi_class_def + "\n"

        # 写入 .pyi 文件
        file_name = self._camel_to_snake(class_name) + '.pyi'
        file_path = os.path.join(self.schema_dir, file_name)

        self._write_generated(file_path, content)

    def _generate_namespace_pyi(self, ns_prefix: str, ns_class_name: str, members: List[Dict[str, Any]]) -> str:
        up = self._package_prefix()
        """生成命名空间类的 .pyi 文件内容"""
        lines = []

        # 收集需要的导入
        imports = [f"from {up}attribute_spec import AttributeSpec"]
        if any('type' not in member for member in members):
            imports.append(f"from {up}relationship_spec import RelationshipSpec")
        needed_types = set()

        for member in members:
            if 'type' in member:  # 是属性
                py_type = self._usd_type_to_python_type(member['type'])
                self._collect_needed_types(py_type, needed_types)

        gf_imports = sorted(needed_types & self.gf_types)
        dtypes_imports = sorted(needed_types & self.dtypes_types)
        common_imports = sorted(needed_types & self.common_types)

        if gf_imports:
            imports.append(f"from {up}gf import {', '.join(gf_imports)}")
        if dtypes_imports:
            imports.append(f"from {up}dtypes import {', '.join(dtypes_imports)}")
        if common_imports:
            imports.append(f"from {up}common import {', '.join(common_imports)}")

        if any(member.get('type', '').endswith('[]') for member in members if 'type' in member):
            imports.append("from typing import List")

        # 生成 allowedTokens 对应的枚举类
        token_classes, imported_token_classes = self._generate_token_classes(members)
        if token_classes:
            imports.append("from enum import ReprEnum")

        # Enums that already live in common.py (Axis, Kind) are referenced by the
        # member signatures below rather than emitted here, so they have to be
        # imported. The member type is plain `token` in the schema, which is why
        # collecting needed types from the types alone never finds them.
        if imported_token_classes:
            imports.append(f"from {up}common import {', '.join(sorted(set(imported_token_classes)))}")

        # 类声明
        lines.append("\n".join(imports))
        lines.append("")
        lines.append("")
        lines.append(f"class {ns_class_name}(AttributeSpec):")

        if token_classes:
            lines.append("")
            lines.extend(token_classes)

        lines.append("")

        # 生成子属性和关系的签名
        declared = 0
        for member in members:
            if 'type' in member:  # 是属性
                signature = self._generate_pyi_attribute_signature('', member, is_sub_attr=True)
            else:  # 是关系
                signature = self._generate_pyi_relationship_signature(ns_prefix, member)
            if signature:
                declared += len(signature)
            lines.extend(signature)

        if declared == 0:
            # Every member was skipped -- a reserved name is dropped, and
            # colorSpace:name is exactly that. A stub with nothing in it is not worth
            # writing, and an empty class body is not valid Python anyway.
            return ""

        return "\n".join(lines)

    def _collect_class_namespace_prefixes(self, class_info: Dict[str, Any]) -> Set[str]:
        prefixes = set()

        for attr in class_info['attributes']:
            full_name = attr.get('full_name', attr['name'])
            if ':' in full_name:
                prefixes.add(full_name.split(':')[0])

        for rel in class_info['relationships']:
            full_name = rel.get('full_name', rel['name'])
            if ':' in full_name:
                prefixes.add(full_name.split(':')[0])

        return prefixes

    def _generate_pyi_imports(self, base_class: str, class_info: Dict[str, Any], imported_token_classes: List[str], generated_ns_files: Optional[Set[str]] = None) -> str:
        up = self._package_prefix()
        """生成 .pyi 文件的导入语句"""
        imports = []

        # 基类导入
        if base_class in ['Typed', 'APISchemaBase']:
            if base_class == 'Typed':
                imports.append(f"from {up}typed import Typed")
            else:
                imports.append(f"from {up}api_schema_base import APISchemaBase")
        else:
            # 同一 schema 目录内的基类用同目录相对导入。这个判断必须排在下面的
            # 跨模块表之前：那张表把这些基类统统硬编码到 geom/ 下，于是生成
            # geom/xformable.py 时会产出 from ..geom.imageable import Imageable，
            # 让一个模块导入它自己。
            if base_class in self.classes_info:
                imports.append(
                    f"from .{self._camel_to_snake(base_class)} import {base_class}")
            else:
                # 跨模块继承
                cross_module_bases = {
                    'Imageable': ('geom', 'Imageable'),
                    'Gprim': ('geom', 'Gprim'),
                    'Boundable': ('geom', 'Boundable'),
                    'Xformable': ('geom', 'Xformable'),
                    'PointBased': ('geom', 'PointBased'),
                    'GeomModelAPI': ('geom', 'GeomModelAPI'),
                    'PrimvarsAPI': ('geom', 'PrimvarsAPI'),
                    'VisibilityAPI': ('geom', 'VisibilityAPI'),
                    'MotionAPI': ('geom', 'MotionAPI'),
                    'XformCommonAPI': ('geom', 'XformCommonAPI'),
                }

                if base_class in cross_module_bases:
                    module, cls = cross_module_bases[base_class]
                    imports.append(f"from ..{module}.{self._camel_to_snake(cls)} import {cls}")
                else:
                    imports.append(f"from .{self._camel_to_snake(base_class)} import {base_class}")

        # 添加常用导入
        if class_info['attributes'] or class_info['relationships']:
            if class_info['attributes']:
                imports.append(f"from {up}attribute_spec import AttributeSpec")
            if class_info['relationships']:
                imports.append(f"from {up}relationship_spec import RelationshipSpec")

            # 收集所有需要的类型
            needed_types = set()
            for attr in class_info['attributes']:
                py_type = self._usd_type_to_python_type(attr['type'])
                if attr.get('allowed_tokens'):
                    class_name = self._snake_to_pascal(attr['name'])
                    py_type = class_name
                self._collect_needed_types(py_type, needed_types)

            if any(attr['type'].endswith('[]') for attr in class_info['attributes']):
                imports.append("from typing import List")

            # 检查是否有 allowedTokens，需要导入 token
            has_allowed_tokens = any(attr.get('allowed_tokens') for attr in class_info['attributes'])
            if has_allowed_tokens:
                needed_types.add('token')

            gf_imports = sorted(needed_types & self.gf_types)
            dtypes_imports = sorted(needed_types & self.dtypes_types)
            common_imports = sorted(needed_types & self.common_types)

            if gf_imports:
                imports.append(f"from {up}gf import {', '.join(gf_imports)}")
            if dtypes_imports:
                imports.append(f"from {up}dtypes import {', '.join(dtypes_imports)}")
            if common_imports:
                imports.append(f"from {up}common import {', '.join(common_imports)}")

        # 添加从 common 导入的枚举类
        if imported_token_classes:
            imports.append(f"from {up}common import {', '.join(sorted(set(imported_token_classes)))}")

        # The stub re-emits the allowedTokens enumerations, which now name ReprEnum
        # themselves because dtypes.token is a plain str subclass rather than an Enum.
        emitted, _ = self._generate_token_classes(class_info['attributes'])
        if emitted and "from enum import ReprEnum" not in imports:
            imports.insert(0, "from enum import ReprEnum")

        # A nested schema declaration is re-emitted as a property here, so the stub has
        # to import the class it names. _generate_imports finds it for the .py from the
        # assignment `XformOp()`; a stub has no assignment, so it cannot.
        #
        # It is a property rather than a bare annotation because PropertySpec defines
        # __get__ and __set__: a class attribute annotated with one of those is a
        # descriptor, and ty checks the access against __get__'s first parameter, which
        # is a PrimSpec -- not the Prim that Prim.__getattr__ hands out. Every other
        # member in these stubs is a property for the same reason.
        for _attr_name, class_name, nested_module in self.NESTED_SCHEMA_DECLARATIONS.get(
                class_info['name'], ()):
            line = f"from .{nested_module} import {class_name}"
            if line not in imports:
                imports.append(line)

        # 添加命名空间类的导入
        if generated_ns_files:
            used_ns_files = self._collect_class_namespace_prefixes(class_info) & generated_ns_files
            for ns_prefix in sorted(used_ns_files):
                ns_class_name = self._snake_to_pascal(ns_prefix)
                imports.append(f"from .{self._camel_to_snake(ns_prefix)} import {ns_class_name}")

        return "\n".join(imports)

    def _generate_imports(self, base_class: str, class_info: Dict[str, Any]) -> str:
        up = self._package_prefix()
        """生成导入语句"""
        imports = []

        # 基类导入
        if base_class in ['Typed', 'APISchemaBase']:
            if base_class == 'Typed':
                imports.append(f"from {up}typed import Typed")
            else:
                imports.append(f"from {up}api_schema_base import APISchemaBase")
        else:
            # 同一 schema 目录内的基类用同目录相对导入。这个判断必须排在下面的
            # 跨模块表之前：那张表把这些基类统统硬编码到 geom/ 下，于是生成
            # geom/xformable.py 时会产出 from ..geom.imageable import Imageable，
            # 让一个模块导入它自己。
            if base_class in self.classes_info:
                imports.append(
                    f"from .{self._camel_to_snake(base_class)} import {base_class}")
            else:
                # 跨模块继承
                cross_module_bases = {
                    'Imageable': ('geom', 'Imageable'),
                    'Gprim': ('geom', 'Gprim'),
                    'Boundable': ('geom', 'Boundable'),
                    'Xformable': ('geom', 'Xformable'),
                    'PointBased': ('geom', 'PointBased'),
                    'GeomModelAPI': ('geom', 'GeomModelAPI'),
                    'PrimvarsAPI': ('geom', 'PrimvarsAPI'),
                    'VisibilityAPI': ('geom', 'VisibilityAPI'),
                    'MotionAPI': ('geom', 'MotionAPI'),
                    'XformCommonAPI': ('geom', 'XformCommonAPI'),
                }

                if base_class in cross_module_bases:
                    module, cls = cross_module_bases[base_class]
                    imports.append(f"from ..{module}.{self._camel_to_snake(cls)} import {cls}")
                else:
                    imports.append(f"from .{self._camel_to_snake(base_class)} import {base_class}")

        # 添加常用导入
        if class_info['attributes'] or class_info['relationships']:
            imports.append(f"from {up}attribute_spec import AttributeSpec")
            if class_info['relationships']:
                imports.append(f"from {up}relationship_spec import RelationshipSpec")

            # 检查是否需要 List（只有当有数组类型属性时才需要）
            has_array = any(attr['type'].endswith('[]') for attr in class_info['attributes'])
            if has_array:
                imports.append("from typing import List")

            # 检查是否需要 namespace 类型（属性或关系有命名空间前缀）
            has_namespace_attrs = any(attr.get('full_name', '').count(':') > 0 for attr in class_info['attributes'])
            has_namespace_rels = any(rel.get('full_name', '').count(':') > 0 for rel in class_info['relationships'])
            if has_namespace_attrs or has_namespace_rels:
                imports.append(f"from {up}dtypes import namespace")

            # 收集所有需要的类型
            needed_types = set()
            for attr in class_info['attributes']:
                py_type = self._usd_type_to_python_type(attr['type'])
                if attr.get('allowed_tokens'):
                    class_name = self._snake_to_pascal(attr['name'])
                    py_type = class_name
                self._collect_needed_types(py_type, needed_types)

            # 检查是否有 allowedTokens，需要导入 token
            has_allowed_tokens = any(attr.get('allowed_tokens') for attr in class_info['attributes'])
            if has_allowed_tokens:
                needed_types.add('token')

            needed_gf_types = needed_types & self.gf_types
            if needed_gf_types:
                imports.append(f"from {up}gf import {', '.join(sorted(needed_gf_types))}")

            needed_dtype_types = needed_types & self.dtypes_types
            if needed_dtype_types:
                imports.append(f"from {up}dtypes import {', '.join(sorted(needed_dtype_types))}")

            # 嵌套 schema 的导入（见 NESTED_SCHEMA_DECLARATIONS）
            for _attr_name, nested_class, nested_module in self.NESTED_SCHEMA_DECLARATIONS.get(
                    class_info['name'], ()):
                imports.append(f"from .{nested_module} import {nested_class}")

        # SchemaKind 的导入与返回必须在上面的条件之外：34 个类既没有属性也没有
        # relationship（Scope、Xform、Volume、各类 API schema 等），return 缩进在
        # 条件块里会让它们拿到 None 而不是导入列表。
        imports.append(f"from {up}common import SchemaKind")
        return "\n".join(imports)

    def _collect_needed_types(self, py_type: str, needed_types: Set[str]) -> None:
        """收集需要的类型"""
        if py_type.startswith('List['):
            inner_type = py_type[5:-1]
            self._collect_needed_types(inner_type, needed_types)
        else:
            needed_types.add(py_type)

    def _generate_class_definition(self, class_info: Dict[str, Any]) -> str:
        """生成类定义"""
        lines = []

        # 类声明
        lines.append(f"class {class_info['name']}({self._determine_base_class(class_info)}):")

        # docstring（类级别使用 4 空格缩进）
        if class_info['doc']:
            doc_str = self._format_class_doc_string(class_info['doc'])
            lines.append(doc_str)
            lines.append("")  # docstring 后加空行

        # schema_kind
        schema_kind = self._determine_schema_kind(class_info)
        lines.append(f"    schema_kind: SchemaKind = {schema_kind}")

        # 如果有 metadata，添加 meta
        if class_info.get('metadata'):
            lines.append("")
            meta_str = self._format_metadata(class_info['metadata'], indent_level=0)
            meta_lines = meta_str.split('\n')
            for i, line in enumerate(meta_lines):
                if i == 0:
                    lines.append(f"    meta = {line}")
                else:
                    lines.append(f"    {line}")

        # 生成 allowedTokens 对应的枚举类
        token_classes, imported_token_classes = self._generate_token_classes(class_info['attributes'])
        if token_classes:
            lines.append("")
            lines.extend(token_classes)

        # 按命名空间分组属性
        namespaced_attrs = {}
        regular_attrs = []

        for attr in class_info['attributes']:
            full_name = attr.get('full_name', attr['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_attrs:
                    namespaced_attrs[ns_prefix] = []
                namespaced_attrs[ns_prefix].append(attr)
            else:
                regular_attrs.append(attr)

        # A schema may declare both ``ns:member`` and a plain member called ``ns``
        # (LightListAPI has lightList:cacheBehavior plus a lightList relationship).
        # The namespace attribute already claims that name, so the plain member is
        # dropped instead of being assigned over it with an incompatible type.
        # The relationship grouping below reuses this, so it is filled in after
        # namespaced_rels is known.
        taken_names = set(namespaced_attrs.keys())

        # A schema may declare both ``ns:member`` and a plain member called ``ns``.
        # UsdGeomCamera does exactly that: a legacy top-level ``float exposure``
        # alongside the ``exposure:`` namespace, and pxr reports both. So the group
        # head takes the plain member's type instead of the namespace sentinel, which
        # is also what lets declared_leaf_names report the head as a property of its
        # own rather than only its children.
        plain_by_name = {attr['name']: attr for attr in regular_attrs}

        # 生成命名空间属性
        for ns_prefix, attrs in namespaced_attrs.items():
            lines.append("")
            head = plain_by_name.get(ns_prefix)
            if head is not None:
                head_type = self._usd_type_to_python_type(head['type'])
                lines.append(
                    f"    {ns_prefix}: AttributeSpec[{head_type}] = AttributeSpec({head_type}, "
                    f"is_leaf=False)")
            else:
                lines.append(f"    {ns_prefix}: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)")

            for attr in attrs:
                lines.append(self._generate_namespaced_attribute_definition(ns_prefix, attr))

        # 生成普通属性
        # 这一段必须在上面的命名空间循环之外：它此前缩进在循环体里，于是只有「恰好含有
        # 命名空间属性」的类才会吐出普通属性。Xformable 没有命名空间属性，于是
        # xformOpOrder 连同下面的嵌套声明一起消失。
        for attr in regular_attrs:
            if attr['name'] in taken_names:
                continue
            lines.append("")
            lines.append(self._generate_attribute_definition(attr))

        # 嵌套 schema 声明（见 NESTED_SCHEMA_DECLARATIONS）
        for attr_name, class_name, _module in self.NESTED_SCHEMA_DECLARATIONS.get(
                class_info['name'], ()):
            if attr_name in taken_names:
                continue
            taken_names.add(attr_name)
            lines.append("")
            lines.append(f"    {attr_name}: {class_name} = {class_name}()")


        # 按命名空间分组关系
        namespaced_rels = {}
        regular_rels = []

        for rel in class_info['relationships']:
            full_name = rel.get('full_name', rel['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_rels:
                    namespaced_rels[ns_prefix] = []
                namespaced_rels[ns_prefix].append(rel)
            else:
                regular_rels.append(rel)

        # 合并命名空间的属性和关系
        taken_names |= set(namespaced_rels.keys())

        # 生成命名空间关系
        for ns_prefix, rels in namespaced_rels.items():
            # 检查是否已经生成了该命名空间的属性声明
            has_ns_attr = any(f"{ns_prefix}: AttributeSpec[namespace]" in line for line in lines)
            if not has_ns_attr:
                lines.append("")
                lines.append(f"    {ns_prefix}: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)")

            for rel in rels:
                lines.append(self._generate_namespaced_relationship_definition(ns_prefix, rel))

        # 生成普通关系
        for rel in regular_rels:
            if rel['name'] in taken_names:
                continue

            lines.append("")
            lines.append(self._generate_relationship_definition(rel))

        return "\n".join(lines)

    def _generate_pyi_class_definition(self, class_name: str, base_class: str, class_info: Dict[str, Any], generated_ns_files: Optional[Set[str]] = None) -> str:
        """生成 .pyi 文件的类定义（只有签名）"""
        lines = []

        # 类声明
        lines.append(f"class {class_name}({base_class}):")

        # docstring
        if class_info['doc']:
            doc_str = self._format_class_doc_string(class_info['doc'])
            lines.append(doc_str)
            lines.append("")  # docstring 后加空行

        # 生成 allowedTokens 对应的枚举类
        token_classes, _ = self._generate_token_classes(class_info['attributes'])
        if token_classes:
            lines.append("")
            lines.extend(token_classes)

        # 按命名空间分组属性和关系
        namespaced_attrs = {}
        regular_attrs = []
        namespaced_rels = {}
        regular_rels = []

        for attr in class_info['attributes']:
            full_name = attr.get('full_name', attr['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_attrs:
                    namespaced_attrs[ns_prefix] = []
                namespaced_attrs[ns_prefix].append(attr)
            else:
                regular_attrs.append(attr)

        for rel in class_info['relationships']:
            full_name = rel.get('full_name', rel['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_rels:
                    namespaced_rels[ns_prefix] = []
                namespaced_rels[ns_prefix].append(rel)
            else:
                regular_rels.append(rel)

        # 合并命名空间的属性和关系
        all_namespaced = set(list(namespaced_attrs.keys()) + list(namespaced_rels.keys()))

        # 生成命名空间属性的签名
        for ns_prefix in all_namespaced:
            attrs = namespaced_attrs.get(ns_prefix, [])
            rels = namespaced_rels.get(ns_prefix, [])

            # 如果生成了独立的命名空间文件，使用命名空间类进行注解
            if generated_ns_files and ns_prefix in generated_ns_files:
                ns_class_name = self._snake_to_pascal(ns_prefix)
                lines.append("    @property")
                lines.append(f"    def {ns_prefix}(self) -> {ns_class_name}: ...")
                lines.append("")
            else:
                # 否则为每个子属性/关系生成单独的签名
                for attr in attrs:
                    lines.extend(self._generate_pyi_attribute_signature(ns_prefix, attr))
                for rel in rels:
                    lines.extend(self._generate_pyi_relationship_signature(ns_prefix, rel))

        # 生成普通属性的签名
        # A schema may declare both ``ns:member`` and a plain member called ``ns``
        # (LightListAPI has lightList:cacheBehavior plus a lightList relationship).
        # The namespace property already occupies that name, so the plain member
        # is dropped rather than emitted twice with different return types.
        taken_names = {
            ns_prefix
            for ns_prefix in all_namespaced
            if generated_ns_files and ns_prefix in generated_ns_files
        }

        for attr in regular_attrs:
            if attr['name'] in taken_names:
                continue

            lines.extend(self._generate_pyi_attribute_signature('', attr))

        # 生成普通关系的签名
        for rel in regular_rels:
            if rel['name'] in taken_names:
                continue

            lines.extend(self._generate_pyi_relationship_signature('', rel))

        # 嵌套 schema 声明（见 NESTED_SCHEMA_DECLARATIONS）
        #
        # This has to be here as well as in the class file. A stub shadows the module it
        # sits beside, so a member the .py declares but the .pyi omits is not merely
        # untyped -- it is invisible, and attribute access silently falls through to
        # Prim.__getattr__, which is typed Any. That is how `xformOp` ended up with no
        # type at all while radius, extent and xformOpOrder all had one: the
        # declaration was in xformable.py the whole time and xformable.pyi never had it.
        for attr_name, class_name, _module in self.NESTED_SCHEMA_DECLARATIONS.get(
                class_info['name'], ()):
            if attr_name in taken_names:
                continue

            taken_names.add(attr_name)
            lines.append("    @property")
            lines.append(f"    def {attr_name}(self) -> {class_name}: ...")
            lines.append("")
            lines.append(f"    @{attr_name}.setter")
            lines.append(f"    def {attr_name}(self, value:{class_name})->None: ...")
            lines.append("")

        # 如果类定义没有任何内容，添加 pass
        if len(lines) == 1:  # 只有类声明行
            lines.append("    pass")

        return "\n".join(lines)


    def _generate_pyi_attribute_signature(self, ns_prefix: str, attr: Dict[str, Any], is_sub_attr: bool = False) -> List[str]:
        """生成属性的 @property 和 setter 签名"""
        lines = []

        # 获取属性名
        full_name = attr.get('full_name', attr['name'])
        if ':' in full_name and ns_prefix:
            attr_name = ':'.join(full_name.split(':')[1:])
            attr_name = attr_name.replace(':', '.')
        else:
            attr_name = attr['name']

        # 转换类型
        py_type = self._usd_type_to_python_type(attr['type'])

        # 如果有 allowedTokens，使用生成的类名
        if attr.get('allowed_tokens'):
            class_name = self._snake_to_pascal(attr['name'])
            py_type = class_name

        # 检查是否与 AttributeSpec/PropertySpec 类的属性名冲突
        reserved_attrs = {
            'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim',
            'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state',
            'custom', 'timeSamples', 'type_name', 'is_namespace'
        }
        is_reserved = attr_name in reserved_attrs

        # 如果是保留字，跳过（在 .pyi 中不生成）
        if is_reserved:
            return []

        # 生成 docstring
        doc_lines = []
        if attr['doc']:
            doc_lines.append(f'        """{attr["doc"]}"""')

        # 生成 @property getter
        lines.append("    @property")
        lines.append(f"    def {attr_name}(self)->AttributeSpec[{py_type}]:")
        if doc_lines:
            lines.extend(doc_lines)
        else:
            lines.append("        ...")
        lines.append("")

        # 生成 setter
        lines.append(f"    @{attr_name}.setter")
        lines.append(f"    def {attr_name}(self, value:{py_type})->None: ...")
        lines.append("")

        return lines

    def _generate_pyi_relationship_signature(self, ns_prefix: str, rel: Dict[str, Any]) -> List[str]:
        """生成关系的 @property 和 setter 签名"""
        lines = []

        # 获取关系名
        full_name = rel.get('full_name', rel['name'])
        if ':' in full_name and ns_prefix:
            rel_name = ':'.join(full_name.split(':')[1:])
            rel_name = rel_name.replace(':', '.')
        else:
            rel_name = rel['name']

        # 生成 docstring
        doc_lines = []
        if rel['doc']:
            doc_lines.append(f'        """{rel["doc"]}"""')

        # 生成 @property getter
        lines.append("    @property")
        lines.append(f"    def {rel_name}(self)->RelationshipSpec:")
        if doc_lines:
            lines.extend(doc_lines)
        else:
            lines.append("        ...")
        lines.append("")

        # 生成 setter
        lines.append(f"    @{rel_name}.setter")
        lines.append(f"    def {rel_name}(self, value:RelationshipSpec)->None: ...")
        lines.append("")

        return lines

    def _generate_token_classes(self, attributes: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """为有 allowedTokens 的属性生成 token 枚举类"""
        lines = []
        imported_classes = []

        # common.py 中已定义的枚举类
        common_enums = {'Axis', 'Kind'}

        for attr in attributes:
            if attr.get('allowed_tokens'):
                class_name = self._snake_to_pascal(attr['name'])

                if class_name in common_enums:
                    imported_classes.append(class_name)
                else:
                    # ReprEnum is explicit because dtypes.token is no longer one. It
                    # is a plain str subclass -- an Enum metaclass intercepts
                    # construction, so token("default") raised -- which makes token a
                    # usable *base* for these enumerations but not an Enum itself.
                    lines.append(f"    class {class_name}(token, ReprEnum):")
                    for token_value in attr['allowed_tokens']:
                        const_name = self._token_to_constant(token_value)
                        lines.append(f"        {const_name} = \"{token_value}\"")

                    lines.append("")

        return lines, imported_classes

    def _generate_namespaced_attribute_definition(self, ns_prefix: str, attr: Dict[str, Any]) -> str:
        """生成命名空间属性的子属性定义"""
        py_type = self._usd_type_to_python_type(attr['type'])

        # 如果有 allowedTokens，使用生成的类名
        if attr.get('allowed_tokens'):
            class_name = self._snake_to_pascal(attr['name'])
            py_type = class_name

        full_name = attr.get('full_name', attr['name'])
        if ':' in full_name:
            sub_attr_name = ':'.join(full_name.split(':')[1:])
        else:
            sub_attr_name = attr['name']

        # 检查是否与 AttributeSpec/PropertySpec 类的属性名冲突
        reserved_attrs = {
            'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim',
            'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state',
            'custom', 'timeSamples', 'type_name', 'is_namespace'
        }
        is_reserved = sub_attr_name in reserved_attrs

        params_list = []
        if attr['is_uniform']:
            params_list.append("uniform=True")
        if attr['default_value'] is not None:
            py_value = self._usd_value_to_python(attr['default_value'])
            params_list.append(f"value={py_value}")
        if attr['doc']:
            doc_str = self._format_doc_string(attr['doc'])
            params_list.append(f"doc={doc_str}")
        if attr.get('metadata'):
            metadata_str = self._format_metadata(attr['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")

        # 如果是保留字，使用 create_prop 方法
        if is_reserved:
            params_list.insert(0, f'name="{sub_attr_name}"')
            params = ', '.join(params_list)
            if '\n' in params or len(params) > 80:
                result = f"    {ns_prefix}.create_prop(AttributeSpec({py_type}"
                result += ",\n"
                for i, param in enumerate(params_list):
                    result += f"        {param}"
                    if i < len(params_list) - 1:
                        result += ",\n"
                    else:
                        result += "\n"
                result += "    ))"
                return result
            else:
                return f"    {ns_prefix}.create_prop(AttributeSpec({py_type}, {params}))"
        else:
            params = ', '.join(params_list)
            if '\n' in params or len(params) > 80:
                result = f"    {ns_prefix}.{sub_attr_name.replace(':', '.')} = AttributeSpec({py_type}"
                if params_list:
                    result += ",\n"
                    for i, param in enumerate(params_list):
                        result += f"        {param}"
                        if i < len(params_list) - 1:
                            result += ",\n"
                        else:
                            result += "\n"
                result += "    )"
                return result
            else:
                return f"    {ns_prefix}.{sub_attr_name.replace(':', '.')} = AttributeSpec({py_type}{', ' + params if params else ''})"

    def _generate_attribute_definition(self, attr: Dict[str, Any]) -> str:
        """生成属性定义"""
        py_type = self._usd_type_to_python_type(attr['type'])

        # 如果有 allowedTokens，使用生成的类名
        if attr.get('allowed_tokens'):
            class_name = self._snake_to_pascal(attr['name'])
            # An array of allowed tokens is still an array. Replacing the whole type
            # with the enum dropped the List, so `token[] x = [...]` was declared as
            # the bare enum and its default could not be converted. Invisible while
            # defaults went unemitted; the stub signature needs the same wrap.
            py_type = f"List[{class_name}]" if attr['type'].endswith('[]') else class_name

        attr_name = attr['name']

        # A leaf attribute is always a plain annotated assignment, even when its name
        # collides with a member of AttributeSpec (name, value, type, uniform, ...). The
        # reserved-name branch used to emit ``{attr_name}.create_prop(...)`` here, but
        # create_prop is an instance method that registers a child on an existing
        # property object: a leaf name is not such an object, so the generated module
        # referenced an undefined name and raised NameError on import. Only a child of
        # a namespace can use that form, and that is a separate code path.
        params_list = []
        if attr['is_uniform']:
            params_list.append("uniform=True")
        # A default parsed from the schema is emitted, so a property the type declares
        # but no layer authored still reads as what the schema says it is. pxr does
        # exactly this and reports it as un-authored; the fallback at the end of
        # composition.resolve_property hands out this declaration, so without the value
        # prim.radius on a fresh Sphere read as None.
        #
        # This used to be suppressed because a token-typed property with a string
        # default could not be constructed: dtypes.token was a ReprEnum with no members,
        # so token("default") raised. token is a plain str subclass now, and the
        # enumerations generated for allowedTokens ask for ReprEnum themselves.
        #
        # An array with no declared default still gets a synthesised empty one, which
        # is what the package has always emitted: xformOpOrder then reads as [] rather
        # than None.
        if attr.get('default_value') is not None:
            params_list.append(f"value={self._format_default_value(attr['default_value'])}")
        elif attr['type'].endswith('[]') and not attr.get('allowed_tokens'):
            params_list.append("value=[]")
        if attr['doc']:
            doc_str = self._format_doc_string(attr['doc'])
            params_list.append(f"doc={doc_str}")
        if attr.get('metadata'):
            metadata_str = self._format_metadata(attr['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")

        params = ', '.join(params_list)
        if '\n' in params or len(params) > 80:
            result = f"    {attr_name}: AttributeSpec[{py_type}] = AttributeSpec({py_type}"
            if params_list:
                result += ",\n"
                for i, param in enumerate(params_list):
                    result += f"        {param}"
                    if i < len(params_list) - 1:
                        result += ",\n"
                    else:
                        result += "\n"
            result += "    )"
            return result

        return (f"    {attr_name}: AttributeSpec[{py_type}] = AttributeSpec({py_type}"
                f"{', ' + params if params else ''})")

    def _format_default_value(self, value: Any) -> str:
        """Render a parsed schema default as Python source.

        The parser has already produced real Python objects, so the only work here is
        choosing a literal that survives a round trip through eval in the generated
        module: a tuple stays a tuple because USDA writes (-1, -1, -1) and USD array
        defaults are tuples, while a str is quoted. Anything unrecognised is rendered
        through repr rather than dropped, so an unexpected shape shows up as a broken
        default instead of a silently missing one.
        """
        if isinstance(value, tuple):
            return "(" + ", ".join(self._format_default_value(item) for item in value) + ")"
        if isinstance(value, list):
            return "[" + ", ".join(self._format_default_value(item) for item in value) + "]"
        if isinstance(value, bool):
            return "True" if value else "False"
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(value, (int, float)):
            return repr(value)

        return repr(value)

    def _generate_relationship_definition(self, rel: Dict[str, Any]) -> str:
        """生成关系定义"""
        params_list = []

        if rel['doc']:
            doc_str = self._format_doc_string(rel['doc'])
            params_list.append(f"doc={doc_str}")

        if rel.get('metadata'):
            metadata_str = self._format_metadata(rel['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")

        params = ', '.join(params_list)
        if '\n' in params or len(params) > 80:
            result = f"    {rel['name']} = RelationshipSpec("
            if params_list:
                result += "\n"
                for i, param in enumerate(params_list):
                    result += f"        {param}"
                    if i < len(params_list) - 1:
                        result += ",\n"
                    else:
                        result += "\n"
            result += "    )"
            return result
        else:
            return f"    {rel['name']} = RelationshipSpec({params})"

    def _generate_namespaced_relationship_definition(self, ns_prefix: str, rel: Dict[str, Any]) -> str:
        """生成命名空间关系定义"""
        # 获取关系的 Python 名称（去掉前缀）
        full_name = rel.get('full_name', rel['name'])
        if ':' in full_name:
            rel_name = ':'.join(full_name.split(':')[1:])
            rel_name = rel_name.replace(':', '.')
        else:
            rel_name = rel['name']

        params_list = []

        if rel['doc']:
            doc_str = self._format_doc_string(rel['doc'])
            params_list.append(f"doc={doc_str}")

        if rel.get('metadata'):
            metadata_str = self._format_metadata(rel['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")

        params = ', '.join(params_list)
        if '\n' in params or len(params) > 80:
            result = f"    {ns_prefix}.{rel_name} = RelationshipSpec("
            if params_list:
                result += "\n"
                for i, param in enumerate(params_list):
                    result += f"        {param}"
                    if i < len(params_list) - 1:
                        result += ",\n"
                    else:
                        result += "\n"
            result += "    )"
            return result
        else:
            return f"    {ns_prefix}.{rel_name} = RelationshipSpec({params})"

    def generate_init_file(self) -> None:
        """生成 __init__.py 文件"""
        lines = []

        # 添加主类的导入（不包含命名空间类）
        for class_name in self.class_names:
            file_name = self._camel_to_snake(class_name)
            lines.append(f"from .{file_name} import {class_name}")

        lines.append("")
        lines.append("__all__ = [")

        # 添加主类到 __all__（不包含命名空间类）
        for class_name in self.class_names:
            lines.append(f'    "{class_name}",')
        lines.append("]")

        init_path = os.path.join(self.schema_dir, '__init__.py')
        self._write_generated(init_path, "\n".join(lines) + "\n")

        print(f"Generated: {init_path}")

    def _usd_type_to_python_type(self, usd_type: str) -> str:
        """转换 USD 类型到 Python 类型"""
        # 处理数组类型
        if usd_type.endswith('[]'):
            base_type = usd_type[:-2]
            return f'List[{base_type}]'

        return usd_type

    def _usd_value_to_python(self, value: Any) -> str:
        """转换 USD 值到 Python 表达式"""
        if value is None:
            return 'None'
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, float):
            if value == float('inf'):
                return "float('inf')"
            elif value == float('-inf'):
                return "float('-inf')"
            return str(value)
        elif isinstance(value, str):
            if '\n' in value or '"' in value:
                # 多行字符串或包含双引号
                if "'" not in value:
                    # 不包含单引号，使用三单引号
                    return f"'''{value}'''"
                else:
                    # 包含单引号，使用三双引号（需要转义内部的双引号）
                    escaped = value.replace('"', '\\"')
                    return f'"""{escaped}"""'
            else:
                return f'"{value}"'
        elif isinstance(value, (list, tuple)):
            # A tuple must go through here too: falling back to str() would emit
            # a bare `inf` for an infinite component, which is not a Python literal.
            items = [self._usd_value_to_python(item) for item in value]
            open_, close = ('[', ']') if isinstance(value, list) else ('(', ')')
            return f"{open_}{', '.join(items)}{close}"
        elif isinstance(value, dict):
            items = [f'"{k}": {self._usd_value_to_python(v)}' for k, v in value.items()]
            return '{' + ', '.join(items) + '}'
        return str(value)

    def _format_class_doc_string(self, doc: str) -> str:
        """格式化类级别的 doc 字符串（4 空格缩进）"""
        if not doc:
            return '    ""'

        if '\n' in doc:
            # 多行 doc，使用三引号，并规范化缩进
            lines = doc.split('\n')
            # 找到最小的非空行缩进
            min_indent = _NO_INDENT
            for line in lines[1:]:  # 跳过第一行
                stripped = line.lstrip()
                if stripped:  # 非空行
                    indent = len(line) - len(stripped)
                    min_indent = min(min_indent, indent)

            # 如果找到最小缩进，去除它
            if min_indent != _NO_INDENT and min_indent > 0:
                normalized_lines = [lines[0]]  # 第一行保持不变
                for line in lines[1:]:
                    if line.strip():  # 非空行
                        normalized_lines.append(line[min_indent:])
                    else:  # 空行
                        normalized_lines.append('')
                dedented_doc = '\n'.join(normalized_lines)
            else:
                dedented_doc = doc

            # 为每行添加 4 个空格缩进（类级别）
            indented_lines = []
            for i, line in enumerate(dedented_doc.split('\n')):
                if i == 0:
                    # 第一行紧跟在三引号后面
                    indented_lines.append('    """' + line)
                else:
                    # 后续行添加 4 个空格缩进
                    indented_lines.append('    ' + line if line else '    ')
            indented_doc = '\n'.join(indented_lines)

            return f'{indented_doc}\n    """'
        else:
            # 单行 doc
            return f'    "{doc}"'

    def _format_doc_string(self, doc: str) -> str:
        """格式化 doc 字符串"""
        if not doc:
            return '""'

        if '\n' in doc:
            # 多行 doc，使用三引号，并规范化缩进
            lines = doc.split('\n')
            # 找到最小的非空行缩进
            min_indent = _NO_INDENT
            for line in lines[1:]:  # 跳过第一行
                stripped = line.lstrip()
                if stripped:  # 非空行
                    indent = len(line) - len(stripped)
                    min_indent = min(min_indent, indent)

            # 如果找到最小缩进，去除它
            if min_indent != _NO_INDENT and min_indent > 0:
                normalized_lines = [lines[0]]  # 第一行保持不变
                for line in lines[1:]:
                    if line.strip():  # 非空行
                        normalized_lines.append(line[min_indent:])
                    else:  # 空行
                        normalized_lines.append('')
                dedented_doc = '\n'.join(normalized_lines)
            else:
                dedented_doc = doc

            # 为每行添加 8 个空格缩进（与代码对齐）
            indented_lines = []
            for i, line in enumerate(dedented_doc.split('\n')):
                if i == 0:
                    # 第一行紧跟在三引号后面
                    indented_lines.append(line)
                else:
                    # 后续行添加 8 个空格缩进
                    indented_lines.append('        ' + line if line else '')
            indented_doc = '\n'.join(indented_lines)

            return f'"""{indented_doc}\n        """'
        else:
            # 单行 doc，使用双引号
            return f'"{doc}"'

    def _format_metadata(self, metadata: Dict[str, Any], indent_level: int = 0) -> str:
        """格式化 metadata 字典"""
        if not metadata:
            return '{}'

        lines = []
        base_indent = '    ' * indent_level
        inner_indent = '    ' * (indent_level + 1)

        lines.append('{')

        items = list(metadata.items())
        for i, (key, value) in enumerate(items):
            comma = ',' if i < len(items) - 1 else ''

            if isinstance(value, dict):
                lines.append(f'{inner_indent}"{key}": {{')
                nested_items = list(value.items())
                for j, (nested_key, nested_value) in enumerate(nested_items):
                    nested_comma = ',' if j < len(nested_items) - 1 else ''
                    if isinstance(nested_value, dict):
                        lines.append(f'{inner_indent}    "{nested_key}": {{')
                        deep_items = list(nested_value.items())
                        for k, (deep_key, deep_value) in enumerate(deep_items):
                            deep_comma = ',' if k < len(deep_items) - 1 else ''
                            lines.append(f'{inner_indent}        "{deep_key}": {self._usd_value_to_python(deep_value)}{deep_comma}')
                        lines.append(f'{inner_indent}    }}{nested_comma}')
                    else:
                        lines.append(f'{inner_indent}    "{nested_key}": {self._usd_value_to_python(nested_value)}{nested_comma}')
                lines.append(f'{inner_indent}}}{comma}')
            else:
                lines.append(f'{inner_indent}"{key}": {self._usd_value_to_python(value)}{comma}')

        lines.append(f'{base_indent}}}')

        return '\n'.join(lines)

    def _camel_to_snake(self, name: str) -> str:
        """将 CamelCase 转换为 snake_case"""
        s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    def _snake_to_pascal(self, name: str) -> str:
        """将 snake_case 或 camelCase 转换为 PascalCase"""
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
        return ''.join(word.capitalize() for word in name.split('_'))

    def _token_to_constant(self, token_value: str) -> str:
        """将 token 值转换为合法的 Python 常量名"""
        if not token_value:
            return 'Empty'

        result = token_value.replace(':', '_').replace('-', '_').replace('.', '_').replace('/', '_')

        if not result or result == '_':
            return 'Unknown'

        if result[0].isdigit():
            result = '_' + result

        result = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', result)

        parts = result.split('_')
        result = ''.join(word.capitalize() for word in parts if word)

        if not result:
            return 'Unknown'

        python_keywords = {'None', 'True', 'False', 'class', 'def', 'return', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass', 'break', 'continue', 'lambda', 'yield', 'global', 'nonlocal', 'assert', 'del', 'raise', 'in', 'is', 'not', 'and', 'or'}
        if result in python_keywords:
            result = result + '_'

        return result
