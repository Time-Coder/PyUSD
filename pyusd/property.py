"""Property: a composed view onto one property of a prim in a stage.

This is the half of USD's property model that a client holds. ``PropertySpec``
and its subclasses are what a layer stores; ``Property`` is what composition
produces from a stack of those. Reads resolve through the engine, including the
schema fallback for a property the type declares but no layer authored; writes
land in the stage's edit layer.

The two concrete kinds are :class:`~pyusd.attribute.Attribute` and
:class:`~pyusd.relationship.Relationship`. Nothing here decides which one a name
means -- :meth:`Property.wrap` looks at the resolved spec -- so a prim attribute
and a stored ``AttributeSpec`` are never confused for one another.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .composition import normalize_prim_path, normalize_property_name
from .property_spec import PropertySpec
from .stage_metadata import StageMetadata
from .utils import in_annotations

if TYPE_CHECKING:
    from .stage import Stage


class Property:
    """A composed property of ``prim_path`` named ``prop_name`` in ``stage``."""

    _stage: Stage
    _prim_path: str
    _prop_name: str

    def __init__(self, stage: Stage, prim_path: str, prop_name: str) -> None:
        self._stage = stage
        self._prim_path = normalize_prim_path(prim_path)
        self._prop_name = normalize_property_name(prop_name)

    # -- which kind of property is this? ------------------------------------

    @classmethod
    def wrap(cls, stage: Stage, prim_path: str, prop_name: str) -> Property:
        """Build the handle that matches what ``prop_name`` resolves to.

        A relationship resolves to ``RelationshipSpec`` and becomes a
        ``Relationship``; anything else, including a name nothing declares and
        nothing authored, becomes an ``Attribute``. That last part is deliberate
        and matches pxr: ``prim.GetAttribute(name)`` on a name that is not there
        returns an invalid ``Usd.Attribute`` rather than None or an error, so
        ``prim.radius = 5`` works on a property nobody has heard of yet. Such a
        handle has ``exists == False`` and still authors.

        The imports are local because every schema class imports ``Prim``, which
        imports this module; module-level imports would close the cycle.
        """
        from .attribute import Attribute
        from .relationship import Relationship
        from .relationship_spec import RelationshipSpec

        prim_path = normalize_prim_path(prim_path)
        prop_name = normalize_property_name(prop_name)
        resolved = stage._engine.resolve_property(prim_path, prop_name)
        if isinstance(resolved, RelationshipSpec):
            return Relationship(stage, prim_path, prop_name)

        return Attribute(stage, prim_path, prop_name)

    # -- identity -----------------------------------------------------------

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def prim_path(self) -> str:
        return self._prim_path

    @property
    def name(self) -> str:
        return self._prop_name.split(":")[-1]

    @property
    def full_name(self) -> str:
        return self._prop_name

    @property
    def path(self) -> str:
        return f"{self._prim_path}.{self._prop_name}"

    @property
    def metadata(self) -> StageMetadata:
        return StageMetadata(self._stage, self._prim_path, self._prop_name)

    @property
    def resolved_property(self) -> Optional[PropertySpec]:
        return self._stage._engine.resolve_property(self._prim_path, self._prop_name)

    @property
    def exists(self) -> bool:
        return self.resolved_property is not None

    def is_valid(self) -> bool:
        """Whether composition found this property.

        The spelling pxr uses; ``exists`` is the property form.
        """
        return self.exists

    @property
    def custom(self) -> bool:
        prop = self.resolved_property
        return prop.custom if prop is not None else True

    @property
    def is_leaf(self) -> bool:
        prop = self.resolved_property
        return prop.is_leaf if prop is not None else True

    @property
    def value_state(self) -> Optional[PropertySpec.ValueState]:
        prop = self.resolved_property
        return prop.value_state if prop is not None else None

    def _value(self) -> Any:
        """The composed value, as the dunders below need it."""
        raise NotImplementedError

    def clear(self) -> None:
        """pxr's Clear(): remove this layer's authored value, keep the spec.

        The spec survives as a bare declaration, so the property keeps existing
        but no longer holds an opinion, and weaker layers or the schema fallback
        compose through again. To author a value block that stops weaker
        opinions instead, use ``Attribute.block``.
        """
        from .attribute_spec import AttributeSpec
        from .relationship_spec import RelationshipSpec

        prop = self._stage._ensure_edit_property(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        if isinstance(prop, AttributeSpec):
            prop.clear()
        elif isinstance(prop, RelationshipSpec):
            prop._targets = []
            prop._value_state = PropertySpec.ValueState.NotAuthored
        else:
            prop._value_state = PropertySpec.ValueState.NotAuthored

        self._stage.invalidate()

    # -- namespace children -------------------------------------------------

    def _declared_child(self, name: str) -> bool:
        """Whether ``name`` is a declared member of this property's namespace.

        Composition only knows about namespaces a layer has materialised, but a
        type can declare children nothing has authored yet -- ``Camera`` declares
        ``exposure:iso`` whether or not a layer ever set it. Both have to count,
        or ``prim.exposure.iso = 1`` would silently do nothing.
        """
        from .schema_registry import schema_type

        type_name = self._stage._engine.resolve_view_type_name(self._prim_path)
        if type_name is None:
            return False

        schema = schema_type(type_name)
        if schema is None:
            return False

        return schema.declared_prop(f"{self._prop_name}:{name}") is not None

    if not TYPE_CHECKING:
        def __getattr__(self, name: str) -> Any:
            if name.startswith("_"):
                # Never proxy dunder/private lookups, or calling the resulting
                # object recurses through this method forever.
                raise AttributeError(name)

            child_name = f"{self._prop_name}:{name}"

            # A nested schema such as XformOp owns its op attributes, so those are
            # real properties rather than attributes of the composed value.
            resolved = self.resolved_property
            if resolved is not None and name in resolved._props:
                return self.wrap(self._stage, self._prim_path, child_name)

            if self._declared_child(name):
                return self.wrap(self._stage, self._prim_path, child_name)

            value = self._value()
            if value is not None and hasattr(value, name):
                return getattr(value, name)

            # Anything else is a mistake rather than an unauthored property: a plain
            # attribute has no members, so `prim.radius.foo` is a typo, and saying so
            # beats handing back a handle to a property named `radius:foo`.
            raise AttributeError(
                f"{type(self).__name__} {self.path!r} has no member {name!r}"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            object.__setattr__(self, name, value)
            return

        # A resolved namespace may be a behavioural property class (XformOp is the
        # motivating case: authoring an op has to update xformOpOrder). Writing
        # through an object installed in the edit layer keeps that behaviour, and
        # installing first is what makes the write stick.
        resolved = self.resolved_property
        if resolved is not None and name in resolved._props:
            edit_prim = self._stage._ensure_edit_prim(self._prim_path)
            installed = self._stage._ensure_edit_property(
                edit_prim, self._prop_name, resolved
            )
            setattr(installed, name, value)
            self._stage.invalidate()
            return

        self._stage._set_property(self._prim_path, f"{self._prop_name}:{name}", value)

    # -- authoring ----------------------------------------------------------

    def rel(self, prim: Any) -> Property:
        """Author this name as a relationship whose first target is ``prim``."""
        return self._stage._create_relationship(self._prim_path, self._prop_name, prim)

    def create(
        self,
        value_type: type,
        value: Any = None,
        uniform: bool = False,
        custom: bool = True,
        fix_type: bool = True,
    ) -> Property:
        return self._stage._create_attribute(
            self._prim_path,
            self._prop_name,
            value_type,
            value=value,
            uniform=uniform,
            custom=custom,
            fix_type=fix_type,
        )

    # -- value-shaped conveniences -----------------------------------------

    def __str__(self) -> str:
        return str(self._value())

    def __repr__(self) -> str:
        return repr(self._value())

    def __bool__(self) -> bool:
        return bool(self._value())

    def __len__(self) -> int:
        return len(self._value())

    def __iter__(self):
        return iter(self._value())

    def __getitem__(self, key: Any) -> Any:
        return self._value()[key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Property):
            other = other._value()

        return self._value() == other

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
