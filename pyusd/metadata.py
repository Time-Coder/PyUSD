from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Dict, Optional

from .dtypes import dictionary
from .metadata_serializer import MetadataSerializer
from .utils import in_annotations

if TYPE_CHECKING:
    pass


class Metadata:

    _parent: Any
    _builtin_data: dictionary
    _custom_data: dictionary
    _builtin_is_set: Dict[str, bool]
    _custom_is_set: Dict[str, bool]

    def __init__(self, parent:Any=None, kwargs:Optional[Dict[str, Any]]=None)->None:
        if kwargs is None:
            kwargs = {}
        self._parent = parent
        self._builtin_data: dictionary = dictionary()
        self._builtin_is_set: Dict[str, bool] = {}
        self._custom_is_set: Dict[str, bool] = {}

        for key, value in kwargs.items():
            if key == "customData":
                if not isinstance(value, dictionary):
                    value = dictionary(value)

                self._custom_data = value
                for sub_key in self._custom_data:
                    self._custom_is_set[sub_key] = False

                continue

            # Nested metadata dicts (assetInfo and friends) are reached with
            # attribute syntax by the schema APIs, which only the dictionary
            # subclass supports.
            if isinstance(value, dict) and not isinstance(value, dictionary):
                value = dictionary(value)

            self._builtin_data[key] = value
            self._builtin_is_set[key] = False

        if "customData" not in kwargs:
            self._custom_data = dictionary()

    def clone(self)->Metadata:
        result = Metadata()
        result._builtin_data = copy.deepcopy(self._builtin_data)
        result._custom_data = copy.deepcopy(self._custom_data)
        result._builtin_is_set = copy.deepcopy(self._builtin_is_set)
        result._custom_is_set = copy.deepcopy(self._custom_is_set)
        return result

    def update(self, kwargs:Dict[str, Any])->None:
        # Read customData without popping it: PrimSpec._fetch_from_class hands this
        # method a schema class's meta dict directly, and popping there stripped
        # customData off the class, so every later application of that same schema
        # raised KeyError.
        custom_data = kwargs.get("customData")

        for key, value in kwargs.items():
            if key == "customData":
                continue

            dictionary.update_one(self._builtin_data, key, value)
            if key not in self._builtin_is_set:
                self._builtin_is_set[key] = False

        if custom_data:
            for key, value in custom_data.items():
                dictionary.update_one(self._custom_data, key, value)
                if key not in self._custom_is_set:
                    self._custom_is_set[key] = False

        self._notify_change()

    @property
    def customData(self)->dictionary:
        return self._custom_data

    def __getattr__(self, name:str)->Any:
        if name in self._builtin_data:
            return self._builtin_data[name]
        elif name in self._custom_data:
            return self._custom_data[name]
        else:
            raise AttributeError(f"current metadata has no attribute '{name}'")

    def __setattr__(self, name:str, value:Any)->None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return

        if name in self._builtin_data:
            self._builtin_data[name] = value
            self._builtin_is_set[name] = True
        else:
            self._custom_data[name] = value
            self._custom_is_set[name] = True

        self._notify_change()

    def _notify_change(self) -> None:
        parent = self._parent
        if parent is not None and hasattr(parent, "_touch"):
            parent._touch()

    def to_str(self, indents:int=0, full:bool=False)->str:
        return MetadataSerializer.to_str(self, indents, full)
