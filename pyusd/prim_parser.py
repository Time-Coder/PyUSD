from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING, Any, Dict, Type

from .attribute_parser import AttributeParser
from .metadata_parser import MetadataParser
from .prim import PrimSpec
from .property import Property
from .relationship_parse import RelationshipParser
from .sdf import Specifier
from .usda_parser import UsdaParser
from .variant_set import VariantSet

if TYPE_CHECKING:
    from tree_sitter import Node


class PrimParser:

    @staticmethod
    def parse(node:Node)->PrimSpec:
        specifier = Specifier.Def
        type_name = ""
        name = ""
        metadata = {}
        block = None

        for child in node.named_children:
            if child.type == "prim_type":
                specifier = PrimParser.specifier_from_text(UsdaParser.node_text(child))
            elif child.type == "identifier":
                type_name = UsdaParser.node_text(child)
            elif child.type == "string":
                name = UsdaParser.load_string(child)
            elif child.type == "metadata":
                metadata = UsdaParser.load_metadata_assignments(child)
            elif child.type == "block":
                block = child

        prim_cls = PrimParser.prim_class(type_name)
        prim = prim_cls(name=name, specifier=specifier)
        PrimParser.apply_loaded_metadata(prim, metadata)

        if block is not None:
            PrimParser.load_block(prim, block)

        return prim

    @staticmethod
    def load_variant_set(parent_prim:PrimSpec, node:Node):
        name = ""
        for child in node.named_children:
            if child.type == "string" and not name:
                name = UsdaParser.load_string(child)
                break

        if not name:
            raise ValueError("variantSet definition has no name")

        variant_set = parent_prim.variant_sets[name]
        for child in node.named_children:
            if child.type == "variant":
                PrimParser.load_variant(variant_set, child)

    @staticmethod
    def load_variant(variant_set:VariantSet, node:Node)->None:
        variant_name = ""
        block = None
        for child in node.named_children:
            if child.type == "string":
                variant_name = UsdaParser.load_string(child)
            elif child.type == "block":
                block = child

        if not variant_name:
            raise ValueError("variant has no name")

        variant = variant_set[variant_name]
        if block is not None:
            PrimParser.load_block(variant, block)

        return variant

    @staticmethod
    def load_block(prim:PrimSpec, node:Node)->None:

        for child in node.named_children:
            if child.type == "prim_definition":
                prim.add_child(PrimParser.parse(child))
            elif child.type in ["attribute_declaration", "attribute_assignment"]:
                PrimParser.create_loaded_prop(prim, AttributeParser.parse(child))
            elif child.type in ["relationship_declaration", "relationship_assignment"]:
                PrimParser.create_loaded_prop(prim, RelationshipParser.parse(child))
            elif child.type == "variant_set_definition":
                PrimParser.load_variant_set(prim, child)

    @staticmethod
    def apply_loaded_metadata(prim:PrimSpec, metadata:Dict[str, Any])->None:
        field_to_attr = {
            "prepend inherits": "_inherits",
            "inherits": "_inherits",
            "prepend references": "_references",
            "references": "_references",
            "prepend payloads": "_payloads",
            "payloads": "_payloads",
            "prepend specializes": "_specializes",
            "specializes": "_specializes",
        }

        remaining = dict(metadata)
        for key, attr_name in field_to_attr.items():
            if key not in remaining:
                continue
            value = remaining.pop(key)
            setattr(prim, attr_name, value if isinstance(value, list) else [value])
            prim.metadata._builtin_is_set[key.split()[-1]] = True

        if "prepend variantSets" in remaining or "variantSets" in remaining:
            value = remaining.pop("prepend variantSets", remaining.pop("variantSets", []))
            value = value if isinstance(value, list) else [value]
            for variant_set_name in value:
                prim.variant_sets[str(variant_set_name)]
            prim.metadata._builtin_is_set["variantSets"] = True

        variants = remaining.pop("variants", None)
        if isinstance(variants, dict):
            for variant_set_name, variant_name in variants.items():
                variant_set = prim.variant_sets[str(variant_set_name)]
                if str(variant_name) not in variant_set:
                    variant_set[str(variant_name)]
                variant_set.select_variant(str(variant_name))
            prim.metadata._builtin_is_set["variants"] = True

        for key, value in remaining.items():
            MetadataParser.set_authored(prim.metadata, key, value)

    @staticmethod
    def create_loaded_prop(prim:PrimSpec, prop:Property)->Property:
        names = prop.name.split(":")
        prop._name = names[-1]
        if len(names) == 1:
            return prim.create_prop(prop)

        current = prim
        for name in names[:-1]:
            if name not in current._props:
                current.create_prop(Property(name, custom=True, is_leaf=False))
            current = current._props[name]

        return current.create_prop(prop)

    @staticmethod
    def specifier_from_text(text:str)->Specifier:
        if text == "class":
            return Specifier.Class
        if text == "over":
            return Specifier.Over
        return Specifier.Def

    @classmethod
    def prim_class(cls, type_name:str)->Type[PrimSpec]:
        if not type_name:
            return PrimSpec

        if not hasattr(cls, "_LOAD_PRIM_TYPES"):
            cls._LOAD_PRIM_TYPES = {"Prim": PrimSpec, "PrimSpec": PrimSpec}
            package = importlib.import_module("pyusd")
            for module_info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                try:
                    module = importlib.import_module(module_info.name)
                except Exception:
                    continue
                for name in getattr(module, "__all__", []):
                    value = getattr(module, name, None)
                    if isinstance(value, type) and issubclass(value, PrimSpec):
                        cls._LOAD_PRIM_TYPES[value.__name__] = value

        return cls._LOAD_PRIM_TYPES.get(type_name, PrimSpec)
