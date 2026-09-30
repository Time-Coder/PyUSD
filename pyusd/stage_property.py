"""StageProperty: a view onto one property of a prim in a stage.

Reads resolve through composition (including the schema fallback for properties
the type declares but no layer authored); writes land in the stage's edit layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .attribute import Attribute
from .composition import normalize_prim_path, normalize_property_name
from .prim_spec import PrimSpec
from .property import Property
from .relationship import Relationship
from .stage_metadata import StageMetadata
from .utils import in_annotations

if TYPE_CHECKING:
    from .stage import Stage

# StageProperty declares a `type` property, which shadows the builtin inside the
# class body, so annotations that mean the builtin go through this alias.
_ValueType = type


class StageProperty:
    _stage: Stage
    _prim_path: str
    _prop_name: str

    @staticmethod
    def _is_path_target(value: Any) -> bool:
        return isinstance(value, str) and (
            value.startswith("<") or value.startswith("/") or value.startswith("@")
        )

    @classmethod
    def _is_relationship_value(cls, value: Any) -> bool:
        from .prim import Prim

        if isinstance(value, (PrimSpec, Prim, Relationship)):
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

        if isinstance(value, Relationship):
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

    @staticmethod
    def _value_of(prop: Optional[Property]) -> Any:
        """The composed value of a resolved property, honouring clear opinions."""
        if prop is None:
            return None

        if isinstance(prop, Attribute):
            if prop.value_state == Property.ValueState.Cleared:
                return None
            return prop.value

        if isinstance(prop, Relationship):
            if prop.value_state == Property.ValueState.Cleared:
                return []
            return prop.targets

        return prop

    def __init__(self, stage: Stage, prim_path: str, prop_name: str) -> None:
        object.__setattr__(self, "_stage", stage)
        object.__setattr__(self, "_prim_path", normalize_prim_path(prim_path))
        object.__setattr__(self, "_prop_name", normalize_property_name(prop_name))

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
    def resolved_property(self) -> Optional[Property]:
        return self._stage._engine.resolve_property(self._prim_path, self._prop_name)

    @property
    def exists(self) -> bool:
        return self.resolved_property is not None

    @property
    def value(self) -> Any:
        return self.get()

    @value.setter
    def value(self, value: Any) -> None:
        self.set(value)

    @property
    def targets(self) -> List[Any]:
        prop = self.resolved_property
        if isinstance(prop, Relationship):
            return prop.targets

        return []

    @property
    def timeSamples(self) -> Dict[float, Any]:
        prop = self.resolved_property
        if isinstance(prop, Attribute):
            return prop.timeSamples

        return {}

    @property
    def value_state(self) -> Optional[Property.ValueState]:
        prop = self.resolved_property
        return prop.value_state if prop is not None else None

    @property
    def type(self) -> Optional[_ValueType]:
        prop = self.resolved_property
        return prop.type if isinstance(prop, Attribute) else None

    @property
    def type_name(self) -> str:
        prop = self.resolved_property
        return prop.type_name if isinstance(prop, Attribute) else ""

    @property
    def custom(self) -> bool:
        prop = self.resolved_property
        return prop.custom if prop is not None else True

    @property
    def is_leaf(self) -> bool:
        prop = self.resolved_property
        return prop.is_leaf if prop is not None else True

    def get(self) -> Any:
        return self._value_of(self.resolved_property)

    def set(self, value: Any) -> None:
        self._stage._set_property(self._prim_path, self._prop_name, value)

    def clear(self) -> None:
        prop = self._stage._ensure_edit_property(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        if isinstance(prop, Attribute):
            prop.clear()
        elif isinstance(prop, Relationship):
            prop._targets = []
            prop._value_state = Property.ValueState.Cleared
        else:
            prop._value_state = Property.ValueState.Cleared
        self._stage.invalidate()

    def create(
        self,
        value_type: _ValueType,
        value: Any = None,
        uniform: bool = False,
        custom: bool = True,
        fix_type: bool = True,
    ) -> StageProperty:
        return self._stage._create_attribute(
            self._prim_path,
            self._prop_name,
            value_type,
            value=value,
            uniform=uniform,
            custom=custom,
            fix_type=fix_type,
        )

    def rel(self, prim: Any) -> StageProperty:
        return self._stage._create_relationship(self._prim_path, self._prop_name, prim)

    def add_target(self, prim: Any) -> None:
        rel = self._stage._ensure_edit_relationship(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        rel._targets.extend(self._coerce_relationship_targets(prim))
        rel._value_state = Property.ValueState.Authored
        self._stage.invalidate()

    def remove_target(self, prim: Any) -> None:
        targets = self._coerce_relationship_targets(prim)
        rel = self._stage._ensure_edit_relationship(
            self._stage._ensure_edit_prim(self._prim_path),
            self._prop_name,
            self.resolved_property,
        )
        for target in targets:
            if target in rel._targets:
                rel._targets.remove(target)
        rel._value_state = Property.ValueState.Authored
        self._stage.invalidate()

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            # Never proxy dunder/private lookups, or calling the resulting
            # object recurses through this method forever.
            raise AttributeError(name)

        child_name = self._prop_name + ":" + name
        if (
            self._stage._engine.resolve_property(self._prim_path, child_name)
            is not None
        ):
            return StageProperty(self._stage, self._prim_path, child_name)

        value = self.get()
        if value is not None and hasattr(value, name):
            return getattr(value, name)

        return StageProperty(self._stage, self._prim_path, child_name)

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

        self._stage._set_property(self._prim_path, self._prop_name + ":" + name, value)

    def __str__(self) -> str:
        return str(self.get())

    def __repr__(self) -> str:
        return repr(self.get())

    def __bool__(self) -> bool:
        return bool(self.get())

    def __len__(self) -> int:
        return len(self.get())

    def __iter__(self):
        return iter(self.get())

    def __getitem__(self, key: Any) -> Any:
        return self.get()[key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StageProperty):
            other = other.get()
        return self.get() == other

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
