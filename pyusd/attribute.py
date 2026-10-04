"""Attribute: a composed property carrying a value.

This is the handle a client holds for something like ``prim.radius``. It is not
an ``AttributeSpec``: that is the stored form, what a layer serialises, and what
``PrimSpec._props`` holds. The two share a shape because composition hands back
the stored object, but they are different things and only one of them is a view.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .attribute_spec import AttributeSpec
from .data import Data, _Arithmetic
from .property import Property
from .property_spec import PropertySpec

# Attribute declares a `type` property, which shadows the builtin inside the
# class body, so annotations that mean the builtin go through this alias.
_ValueType = type


class Attribute(_Arithmetic, Property):
    """A composed attribute: a value, a type, and optionally time samples."""

    @property
    def _attribute(self) -> Optional[AttributeSpec]:
        prop = self.resolved_property
        return prop if isinstance(prop, AttributeSpec) else None

    def _value(self) -> Any:
        prop = self._attribute
        if prop is None:
            return None

        if prop.value_state == PropertySpec.ValueState.Cleared:
            return None

        return prop.value

    def get(self) -> Any:
        return self._value()

    def set(self, value: Any) -> None:
        self._stage._set_property(self._prim_path, self._prop_name, value)

    # -- the three hooks _Arithmetic asks for ---------------------------------
    #
    # Everything above this line is about what an attribute *is*; everything below
    # is what lets it share the arithmetic with Data. Keeping them together makes
    # the whole contract visible in one place.

    def _read(self) -> Any:
        """The composed value. Recomputed per call and never cached."""
        return self._value()

    def _write(self, value: Any) -> None:
        """Where an in-place result lands: a new opinion in the edit layer.

        Not on this object. A handle composes its value out of the layer stack on
        every read, so writing to itself would write to a temporary -- and it would
        miss the edit layer, the invalidation, and the layer strength that decides
        which layer an opinion belongs to.
        """
        self.set(value)

    @staticmethod
    def _other_value(other: Any) -> Any:
        """Unwrap an operand that is itself a handle or a stored spec."""
        if isinstance(other, Property):
            return other._value()

        if isinstance(other, Data):
            return other._raw()

        return other

    @property
    def value(self) -> Any:
        return self.get()

    @value.setter
    def value(self, value: Any) -> None:
        self.set(value)

    @property
    def type(self) -> Optional[_ValueType]:
        return self._attribute._type if self._attribute is not None else None

    @property
    def type_name(self) -> str:
        prop = self._attribute
        return prop.type_name if prop is not None else ""

    @property
    def uniform(self) -> bool:
        prop = self._attribute
        return prop.uniform if prop is not None else False

    @property
    def timeSamples(self) -> Dict[float, Any]:
        prop = self._attribute
        return prop.timeSamples if prop is not None else {}

