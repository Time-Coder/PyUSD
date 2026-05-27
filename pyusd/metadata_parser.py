from __future__ import annotations
from typing import Any, Dict, Optional, Union, TYPE_CHECKING
import tree_sitter

from .metadata import Metadata
from .usda_parser import UsdaParser

if TYPE_CHECKING:
    from .prim import Prim
    from .property import Property


class MetadataParser:

    @staticmethod
    def parse(node:tree_sitter.Node, parent:Optional[Union[Prim, Property]]=None, defaults:Optional[Dict[str, Any]]=None)->Metadata:
        if defaults is None:
            defaults = {}

        result = Metadata(parent, defaults)
        for key, value in UsdaParser.load_metadata_assignments(node).items():
            MetadataParser.set_authored(result, key, value)

        return result
    
    @staticmethod
    def set_authored(metadata:Metadata, key:str, value:Any)->None:
        clean_key = key.split(" ", 1)[1] if key.startswith(("prepend ", "append ")) else key
        metadata.update({key: value})
        if clean_key in metadata._builtin_data:
            metadata._builtin_is_set[clean_key] = True
        else:
            metadata._custom_data[clean_key] = value
            metadata._custom_is_set[clean_key] = True