from typing import Any, Dict, List, Optional

from tree_sitter import Node

from .attribute import Attribute
from .metadata_parser import MetadataParser
from .property import Property
from .usda_parser import UsdaParser


class AttributeParser:

    # Populated on first use by usd_type_registry(); declared here so the
    # attribute exists for type checkers instead of appearing only via hasattr.
    _LOAD_USD_TYPES: Optional[Dict[str, type]] = None

    def parse(node:Node)->Attribute:
        type_name = "token"
        name = ""
        value = None
        has_value = False
        metadata = {}
        uniform = False
        custom = False

        for child in node.named_children:
            if child.type == "attribute_type":
                type_name = UsdaParser.node_text(child)
            elif child.type in ["identifier", "qualified_identifier"]:
                name = UsdaParser.node_text(child)
            elif child.type == "uniform":
                uniform = True
            elif child.type == "custom":
                custom = True
            elif child.type == "metadata":
                metadata = UsdaParser.load_metadata_assignments(child)
            elif UsdaParser.is_value_node(child):
                value = UsdaParser.load_value(child)
                has_value = True

        prop = Attribute(AttributeParser.usd_type(type_name), name=name, value=None, metadata=metadata, uniform=uniform, custom=custom, fix_type=False)
        prop._value = value
        prop._value_state = Property.ValueState.Authored if has_value else Property.ValueState.NotAuthored
        for key, authored_value in metadata.items():
            MetadataParser.set_authored(prop._metadata, key, authored_value)

        return prop

    @staticmethod
    def usd_type(type_name:str)->type:
        array_dim = type_name.count("[]")
        base_name = type_name.replace("[]", "")
        base_type = tuple if base_name == "tuple" else AttributeParser.usd_type_registry().get(base_name, str)

        result: Any = base_type
        for _ in range(array_dim):
            result = List[result]
        return result

    @staticmethod
    def usd_type_registry()->Dict[str, type]:
        if AttributeParser._LOAD_USD_TYPES is None:
            from . import dtypes, gf
            registry: Dict[str, type] = {
                "bool": bool,
                "int": int,
                "float": float,
                "string": str,
                "token": str,
                "dictionary": dict,
            }
            for module in [dtypes, gf]:
                for name in dir(module):
                    value = getattr(module, name)
                    if isinstance(value, type):
                        registry[name] = value
            AttributeParser._LOAD_USD_TYPES = registry

        return AttributeParser._LOAD_USD_TYPES
