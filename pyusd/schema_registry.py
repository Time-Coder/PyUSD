"""Schema type registry.

Maps a USD ``typeName`` onto the Python class that models it, the inheritance
chain recorded in USDA, and the property declarations that class carries. The
registry is the single source of truth for "what does this type look like", and
replaces per-instance materialisation of class level property declarations.

Building it eagerly at import time also removes the previous
``pkgutil.walk_packages`` scan, which ran on every parse and silently swallowed
import errors.
"""

from __future__ import annotations

import contextlib
import importlib
import pkgutil
from typing import Dict, List, Optional

from .common import SchemaKind
from .property_spec import PropertySpec

_PACKAGE = "pyusd"


class SchemaType:
    """Everything derivable from a schema class without instantiating a prim."""

    __slots__ = ("name", "cls", "bases", "declared_props")

    def __init__(
        self,
        name: str,
        cls: Optional[type],
        bases: List[str],
        declared_props: Dict[str, PropertySpec],
    ) -> None:
        self.name = name
        self.cls = cls
        self.bases = bases
        self.declared_props = declared_props

    @property
    def inherits(self) -> List[str]:
        return [f"</{base}>" for base in self.bases]

    def declared_prop(self, prop_name: str) -> Optional[PropertySpec]:
        """Resolve a possibly namespaced declaration, e.g. ``xformOp:translate``."""
        parts = prop_name.split(":")
        current = self.declared_props.get(parts[0])
        if current is None:
            return None

        for part in parts[1:]:
            current = current._props.get(part)
            if current is None:
                return None

        return current

    def declared_leaf_names(self) -> List[str]:
        """Names of declared leaf properties, namespaces expanded to ``ns:leaf``.

        Only a plain ``AttributeSpec`` is expanded. That is a namespace group whose
        children are genuine declared attributes, such as ``primvars`` or
        ``exposure``. ``Xformable`` also declares a non-leaf ``xformOp``, but that
        entry is an ``XformOp`` instance -- a schema over one op attribute, not a
        namespace -- and expanding it would invent 19 ``xformOp:translate``-style
        properties that USD never declares. They come into being when
        ``AddXformOp`` authors them, which is why ``UsdPrim::GetPropertyNames``
        does not report them either. A nested schema is skipped rather than
        reported, since it is not a property name at all.

        A group whose value type is ``dtypes.namespace`` is a pure namespace and
        contributes only its children. Any other group is also a property in its
        own right: ``UsdGeomCamera`` declares a legacy top-level ``float exposure``
        *and* the ``exposure:`` namespace, and the generated class models the legacy
        attribute as the head of the group, so its own name has to be reported too.
        """
        from .attribute_spec import AttributeSpec
        from .dtypes import namespace

        names: List[str] = []

        def walk(props: Dict[str, PropertySpec], prefix: str) -> None:
            for name, prop in props.items():
                full = name if not prefix else f"{prefix}:{name}"
                if not prop.is_leaf and prop._props:
                    if type(prop) is not AttributeSpec:
                        continue
                    if getattr(prop, "_type", None) is not namespace:
                        names.append(full)
                    walk(prop._props, full)
                else:
                    names.append(full)

        walk(self.declared_props, "")
        return names

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"SchemaType({self.name!r}, bases={self.bases!r})"

    @staticmethod
    def _is_schema_class(value: type) -> bool:
        kind = getattr(value, "schema_kind", None)
        if kind is None:
            return False

        # API schemas are applied to a prim, they do not name a type by themselves,
        # so only the typed kinds are registered here.
        return kind in (
            SchemaKind.Invalid,
            SchemaKind.ConcreteTyped,
            SchemaKind.AbstractBase,
            SchemaKind.AbstractTyped,
        )

    @staticmethod
    def _collect_bases(cls: type) -> List[str]:
        """The schema's direct bases, i.e. what USDA records as ``inherits``."""
        bases = []
        for base in cls.__bases__:
            if base.__name__ in ("PrimSpec", "Prim"):
                continue

            bases.append(base.__name__)

        return bases

    @staticmethod
    def _collect_declared_props(cls: type) -> Dict[str, PropertySpec]:
        """Gather property declarations from a schema class, base classes first."""
        declared: Dict[str, PropertySpec] = {}
        for klass in reversed(cls.__mro__):
            if klass is object:
                continue

            for name, value in vars(klass).items():
                if not isinstance(value, PropertySpec):
                    continue

                declared[name] = value

        return declared

    @staticmethod
    def _strip_declarations(cls: type) -> None:
        """Turn a schema class into a pure type marker.

        PropertySpec declarations used to sit on the class itself, which meant every
        instance shared one mutable AttributeSpec and a class attribute would shadow
        per-instance access once the class also served as a stage view. The registry
        now holds the only copy, so the attributes are removed once collected.

        Annotations are deliberately left in place: they are what a type checker and
        an IDE read, and the proxy classes no longer consult them (see
        ``Prim.__setattr__``).
        """
        for klass in cls.__mro__:
            if klass is object:
                continue

            for name, value in list(vars(klass).items()):
                if not isinstance(value, PropertySpec):
                    continue

                with contextlib.suppress(AttributeError, TypeError):
                    delattr(klass, name)


_TYPES: Dict[str, SchemaType] = {}
_BUILT = False
_BUILDING = False


def _build() -> None:
    """Populate the registry once every pyusd module is importable.

    Called from the tail of ``pyusd/__init__.py``. The re-entrancy guard matters:
    importing the submodules below re-enters this module, and a partial table
    cached by that nested call would silently hide every type discovered later.
    """
    global _BUILT, _BUILDING

    if _BUILT or _BUILDING:
        return

    _BUILDING = True
    try:
        types: Dict[str, SchemaType] = {}
        classes: List[type] = []
        package = importlib.import_module(_PACKAGE)
        for module_info in pkgutil.walk_packages(package.__path__, _PACKAGE + "."):
            try:
                module = importlib.import_module(module_info.name)
            except Exception:  # pragma: no cover - optional/unavailable submodules
                continue

            for value in vars(module).values():
                if not isinstance(value, type) or not SchemaType._is_schema_class(value):
                    continue

                if value.__name__ in types or value in classes:
                    continue

                types[value.__name__] = SchemaType(
                    name=value.__name__,
                    cls=value,
                    bases=SchemaType._collect_bases(value),
                    declared_props={},
                )
                classes.append(value)

        # Collect every type before stripping anything: declarations are inherited,
        # so a base class must still carry its attributes when a subclass is read.
        for value in classes:
            types[value.__name__].declared_props = SchemaType._collect_declared_props(value)

        for value in classes:
            SchemaType._strip_declarations(value)

        _TYPES.update(types)
        _BUILT = True
    finally:
        _BUILDING = False


def prim_class(type_name: str) -> Optional[type]:
    """Return the Python class modelling ``type_name``, if one is known."""
    entry = _TYPES.get(type_name)
    return entry.cls if entry is not None else None


def schema_type(type_name: str) -> Optional[SchemaType]:
    """Return the registry entry for ``type_name``, or None when unknown."""
    if not type_name:
        return None

    _build()
    return _TYPES.get(type_name)


def declared_prop(type_name: str, prop_name: str) -> Optional[PropertySpec]:
    entry = schema_type(type_name)
    if entry is None:
        return None

    return entry.declared_prop(prop_name)


def declared_leaf_names(type_name: str) -> List[str]:
    entry = schema_type(type_name)
    if entry is None:
        return []

    return entry.declared_leaf_names()
