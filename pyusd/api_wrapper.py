from typing import Type, TYPE_CHECKING

from .api_schema_base import APISchemaBase

if TYPE_CHECKING:
    from .prim import Prim


class APIWrapper:

    def __init__(self, api_key:str, api_type: Type[APISchemaBase], prim: Prim)->None:
        self._api_key: str = api_key
        self._api_type: Type[APISchemaBase] = api_type
        self._prim: Prim = prim

    def __call__(self, instance_name:str)->APISchemaBase:
        if (self._api_key, instance_name) not in self._prim._apis:
            self._prim._apis[self._api_key, instance_name] = self._api_type(self._prim, instance_name)
        
        return self._prim._apis[self._api_key, instance_name]
        