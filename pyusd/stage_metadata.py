"""StageMetadata: metadata on a composed prim, property, or the layer itself."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .composition import normalize_prim_path, normalize_property_name
from .utils import in_annotations

if TYPE_CHECKING:
    from .stage import Stage


class StageMetadata:
    _stage: Stage
    _prim_path: Optional[str]
    _prop_name: str

    def __init__(
        self, stage: Stage, prim_path: Optional[str], prop_name: str = ""
    ) -> None:
        self._stage = stage
        self._prim_path = normalize_prim_path(prim_path) if prim_path else None
        self._prop_name = normalize_property_name(prop_name) if prop_name else ""

    def get(self, key: str, default: Any = None) -> Any:
        value = self._stage._engine.resolve_metadata(
            self._prim_path, key, self._prop_name
        )
        return default if value is None else value

    def set(self, key: str, value: Any) -> None:
        self._stage._set_metadata(self._prim_path, key, value, self._prop_name)

    if not TYPE_CHECKING:
        def __getattr__(self, name: str) -> Any:
            value = self._stage._engine.resolve_metadata(
                self._prim_path, name, self._prop_name
            )
            if value is None:
                raise AttributeError(name)

            return value

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            object.__setattr__(self, name, value)
            return

        self.set(name, value)
