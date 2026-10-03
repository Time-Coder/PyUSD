"""Attribute: a composed property carrying a value.

This is the handle a client holds for something like ``prim.radius``. It is not
an ``AttributeSpec``: that is the stored form, what a layer serialises, and what
``PrimSpec._props`` holds. The two share a shape because composition hands back
the stored object, but they are different things and only one of them is a view.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .attribute_spec import AttributeSpec
from .property import Property
from .property_spec import PropertySpec

# Attribute declares a `type` property, which shadows the builtin inside the
# class body, so annotations that mean the builtin go through this alias.
_ValueType = type


class Attribute(Property):
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
