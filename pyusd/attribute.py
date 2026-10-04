"""Attribute: a composed property carrying a value.

This is the handle a client holds for something like ``prim.radius``. It is not
an ``AttributeSpec``: that is the stored form, what a layer serialises, and what
``PrimSpec._props`` holds. The two share a shape because composition hands back
the stored object, but they are different things and only one of them is a view.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .attribute_spec import AttributeSpec
from .data import Data
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

    # -- operators ----------------------------------------------------------
    #
    # These used to reach a prim property through Data, which the stored
    # AttributeSpec inherits and a composed handle does not: the split that
    # introduced the view classes routed Prim attribute access to one, and
    # `prim.radius += 1` stopped working without anyone deciding it should. The
    # bodies mirror Data's so the arithmetic agrees with the stored form, with one
    # difference that only a view can make: an in-place operator authors through
    # set() so the result lands in the edit layer, rather than mutating a spec the
    # caller never asked to change.
    #
    # Data.__setitem__ is deliberately not mirrored. It mutates the value it
    # holds, which is meaningless for a value composed out of a layer stack -- the
    # change has to go through the edit layer -- so element assignment stays on the
    # spec, where it means what it says.

    @staticmethod
    def _other_value(other: Any) -> Any:
        """Unwrap an operand so a handle or a spec contributes its value."""
        if isinstance(other, Property):
            return other._value()

        if isinstance(other, Data):
            return other._raw()

        return other

    def __add__(self, other: Any) -> Any:
        return self._value() + self._other_value(other)

    def __radd__(self, other: Any) -> Any:
        return self._other_value(other) + self._value()

    def __iadd__(self, other: Any) -> Attribute:
        self.set(self._value() + self._other_value(other))
        return self

    def __sub__(self, other: Any) -> Any:
        return self._value() - self._other_value(other)

    def __rsub__(self, other: Any) -> Any:
        return self._other_value(other) - self._value()

    def __isub__(self, other: Any) -> Attribute:
        self.set(self._value() - self._other_value(other))
        return self

    def __mul__(self, other: Any) -> Any:
        return self._value() * self._other_value(other)

    def __rmul__(self, other: Any) -> Any:
        return self._other_value(other) * self._value()

    def __imul__(self, other: Any) -> Attribute:
        self.set(self._value() * self._other_value(other))
        return self

    def __truediv__(self, other: Any) -> Any:
        return self._value() / self._other_value(other)

    def __rtruediv__(self, other: Any) -> Any:
        return self._other_value(other) / self._value()

    def __itruediv__(self, other: Any) -> Attribute:
        self.set(self._value() / self._other_value(other))
        return self

    def __floordiv__(self, other: Any) -> Any:
        return self._value() // self._other_value(other)

    def __rfloordiv__(self, other: Any) -> Any:
        return self._other_value(other) // self._value()

    def __ifloordiv__(self, other: Any) -> Attribute:
        self.set(self._value() // self._other_value(other))
        return self

    def __mod__(self, other: Any) -> Any:
        return self._value() % self._other_value(other)

    def __rmod__(self, other: Any) -> Any:
        return self._other_value(other) % self._value()

    def __imod__(self, other: Any) -> Attribute:
        self.set(self._value() % self._other_value(other))
        return self

    def __pow__(self, other: Any) -> Any:
        return self._value() ** self._other_value(other)

    def __rpow__(self, other: Any) -> Any:
        return self._other_value(other) ** self._value()

    def __ipow__(self, other: Any) -> Attribute:
        self.set(self._value() ** self._other_value(other))
        return self

    def __lt__(self, other: Any) -> bool:
        return self._value() < self._other_value(other)

    def __rlt__(self, other: Any) -> bool:
        return self._other_value(other) < self._value()

    def __gt__(self, other: Any) -> bool:
        return self._value() > self._other_value(other)

    def __rgt__(self, other: Any) -> bool:
        return self._other_value(other) > self._value()

    def __le__(self, other: Any) -> bool:
        return self._value() <= self._other_value(other)

    def __rle__(self, other: Any) -> bool:
        return self._other_value(other) <= self._value()

    def __ge__(self, other: Any) -> bool:
        return self._value() >= self._other_value(other)

    def __rge__(self, other: Any) -> bool:
        return self._other_value(other) >= self._value()

    def __contains__(self, item: Any) -> bool:
        return self._other_value(item) in self._value()
