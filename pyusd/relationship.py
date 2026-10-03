"""Relationship: a composed property whose value is a list of targets.

A relationship is a property, so it shares :class:`~pyusd.property.Property`'s
identity, validity and authoring rules; what distinguishes it is that its value
is target paths rather than a typed value. Targets are kept in the composed form
USD uses, ``</Path>`` strings for prim targets, and are authored into the edit
layer the same way any other property is.
"""

from __future__ import annotations

from typing import Any, List, Optional

from .composition import normalize_prim_path
from .prim_spec import PrimSpec
from .property import Property
from .property_spec import PropertySpec
from .relationship_spec import RelationshipSpec


class Relationship(Property):
    """A composed relationship: an ordered list of targets."""

    @property
    def _relationship(self) -> Optional[RelationshipSpec]:
        prop = self.resolved_property
        return prop if isinstance(prop, RelationshipSpec) else None

    def _value(self) -> List[Any]:
        prop = self._relationship
        if prop is None:
            return []

        if prop.value_state == PropertySpec.ValueState.Cleared:
            return []

        return prop.targets

    @property
    def targets(self) -> List[Any]:
        return self._value()

    @targets.setter
    def targets(self, value: Any) -> None:
        self.set_targets(value)

    def get_targets(self) -> List[Any]:
        return self._value()

    def set_targets(self, targets: Any) -> None:
        rel = self._edit_relationship()
        rel._targets = self._coerce_relationship_targets(targets)
        rel._value_state = PropertySpec.ValueState.Authored
        self._stage.invalidate()

    def add_target(self, prim: Any) -> None:
        rel = self._edit_relationship()
        rel._targets.extend(self._coerce_relationship_targets(prim))
        rel._value_state = PropertySpec.ValueState.Authored
        self._stage.invalidate()

    def remove_target(self, prim: Any) -> None:
        rel = self._edit_relationship()
        for target in self._coerce_relationship_targets(prim):
            if target in rel._targets:
                rel._targets.remove(target)

        rel._value_state = PropertySpec.ValueState.Authored
        self._stage.invalidate()

    def _edit_relationship(self) -> RelationshipSpec:
        return self._stage._ensure_edit_relationship(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )

    # -- target coercion ----------------------------------------------------
    #
    # Authoring a target accepts what a user has to hand: a Prim, a PrimSpec, a
    # path string, or an already-composed "<path>" / "@layer@path" reference.

    @staticmethod
    def _is_path_target(value: Any) -> bool:
        return isinstance(value, str) and (
            value.startswith("<") or value.startswith("/") or value.startswith("@")
        )

    @classmethod
    def _is_relationship_value(cls, value: Any) -> bool:
        from .prim import Prim

        if isinstance(value, (PrimSpec, Prim, RelationshipSpec)):
            return True

        if isinstance(value, list) and value:
            return all(
                isinstance(item, (PrimSpec, Prim)) or cls._is_path_target(item)
                for item in value
            )

        return cls._is_path_target(value)

    @staticmethod
    def _coerce_relationship_targets(value: Any) -> List[Any]:
        from .prim import Prim

        if isinstance(value, RelationshipSpec):
            return list(value.targets)

        if not isinstance(value, list):
            value = [value]

        result: List[Any] = []
        for item in value:
            if isinstance(item, Prim):
                result.append(f"<{item.path}>")
            elif isinstance(item, PrimSpec):
                result.append(item)
            elif isinstance(item, str):
                if item.startswith("<") or item.startswith("@"):
                    result.append(item)
                else:
                    result.append(f"<{normalize_prim_path(item)}>")
            else:
                result.append(item)

        return result
