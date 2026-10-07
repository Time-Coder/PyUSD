from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, List

from .dtypes import asset, dictionary

if TYPE_CHECKING:
    from tree_sitter import Node


class UsdaParser:

    @staticmethod
    def load_metadata_assignments(node:Node)->Dict[str, Any]:
        result = {}
        for child in node.named_children:
            if child.type != "metadata_assignment":
                continue

            orderer = ""
            key = ""
            value = None
            for assign_child in child.named_children:
                if assign_child.type == "orderer":
                    orderer = UsdaParser.node_text(assign_child)
                elif assign_child.type == "identifier":
                    key = UsdaParser.node_text(assign_child)
                elif UsdaParser.is_value_node(assign_child):
                    value = UsdaParser.load_value(assign_child)

            if key:
                full_key = f"{orderer} {key}" if orderer else key
                result[full_key] = value

        return result

    @staticmethod
    def load_value(node:Node)->Any:
        if node.type == "default_value":
            for child in node.named_children:
                if UsdaParser.is_value_node(child):
                    return UsdaParser.load_value(child)
            return None

        text = UsdaParser.node_text(node)
        if node.type == "string":
            return UsdaParser.load_string(node)
        if node.type == "bool":
            return text == "true"
        if node.type == "None":
            # pxr spells a value block `= None`; that is an authored None, not a
            # missing value, and the text fallback would turn it into the string
            # "None".
            return None
        if node.type in ["int", "integer"]:
            return int(text)
        if node.type == "float":
            if text == "inf":
                return float("inf")
            if text == "-inf":
                return float("-inf")
            return float(text)
        if node.type == "asset_path":
            return asset(text.strip("@"))
        if node.type in ["prim_path", "arc_path"]:
            return text
        if node.type in ["list", "list_proxy", "array"]:
            return [
                UsdaParser.load_value(child)
                for child in node.named_children
                if UsdaParser.is_value_node(child)
            ]
        if node.type == "tuple":
            return tuple(
                UsdaParser.load_value(child)
                for child in node.named_children
                if UsdaParser.is_value_node(child)
            )
        if node.type == "dictionary":
            return dictionary(UsdaParser.load_dictionary(node))

        return text

    @staticmethod
    def load_dictionary(node:Node)->Dict[str, Any]:
        result = {}
        named_children = list(node.named_children)
        index = 0
        while index < len(named_children):
            child = named_children[index]
            if child.type == "dictionary_item":
                key = ""
                value = None
                for item_child in child.named_children:
                    if item_child.type == "identifier":
                        key = UsdaParser.node_text(item_child)
                    elif UsdaParser.is_value_node(item_child):
                        value = UsdaParser.load_value(item_child)
                if key:
                    result[key] = value
                index += 1
                continue

            if child.type == "attribute_type" and index + 2 < len(named_children):
                key_node = named_children[index + 1]
                value_node = named_children[index + 2]
                if key_node.type in ["identifier", "qualified_identifier"] and UsdaParser.is_value_node(value_node):
                    result[UsdaParser.node_text(key_node)] = UsdaParser.load_value(value_node)
                    index += 3
                    continue

            index += 1
        return result

    @staticmethod
    def is_value_node(node:Node)->bool:
        return node.type in {
            "default_value",
            "string",
            "bool",
            "int",
            "integer",
            "float",
            "array",
            "list",
            "list_proxy",
            "tuple",
            "dictionary",
            "arc_path",
            "asset_path",
            "prim_path",
            "None",
        }

    @staticmethod
    def load_string(node:Node)->str:
        text = UsdaParser.node_text(node)
        if (
            (text.startswith("'''") and text.endswith("'''")) or
            (text.startswith('"""') and text.endswith('"""'))
        ):
            return text[3:-3]

        return text.strip('"')

    @staticmethod
    def node_text(node:Node)->str:
        # tree-sitter types Node.text as Optional[bytes]; it is None only for
        # zero-width or error nodes, which we never ask for.
        text = node.text
        return "" if text is None else text.decode("utf-8")

    @staticmethod
    def resolve_asset_path(file_name, rel_path:str)->str:
        if os.path.isabs(rel_path):
            return rel_path

        return os.path.abspath(os.path.dirname(file_name) + "/" + rel_path).replace("\\", "/")

    @staticmethod
    def as_list(value:Any)->List[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]
