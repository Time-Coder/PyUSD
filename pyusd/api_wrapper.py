from __future__ import annotations

from typing import TYPE_CHECKING, Type

from .api_schema_base import APISchemaBase

if TYPE_CHECKING:
    from .prim_spec import PrimSpec


class APIWrapper:

    def __init__(self, api_key:str, api_type: Type[APISchemaBase], prim: PrimSpec)->None:
        self._api_key: str = api_key
        self._api_type: Type[APISchemaBase] = api_type
        self._prim: PrimSpec = prim

    def __call__(self, instance_name:str)->APISchemaBase:
        if (self._api_key, instance_name) not in self._prim._apis:
            self._prim._apis[self._api_key, instance_name] = self._api_type(self._prim, instance_name)

        return self._prim._apis[self._api_key, instance_name]
