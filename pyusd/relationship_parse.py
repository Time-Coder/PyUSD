from tree_sitter import Node

from .metadata_parser import MetadataParser
from .property import Property
from .relationship import Relationship
from .usda_parser import UsdaParser


class RelationshipParser:

    @staticmethod
    def parse(node:Node)->Relationship:
        name = ""
        metadata = {}
        custom = False
        targets = []

        for child in node.named_children:
            if child.type in ["identifier", "qualified_identifier"]:
                name = UsdaParser.node_text(child)
            elif child.type == "custom":
                custom = True
            elif child.type == "metadata":
                metadata = UsdaParser.load_metadata_assignments(child)
            elif child.type in ["prim_path", "arc_path", "list", "list_proxy"]:
                value = UsdaParser.load_value(child)
                targets = value if isinstance(value, list) else [value]

        prop = Relationship(name=name, metadata=metadata, custom=custom)
        if targets:
            prop._targets = targets
            prop._value_state = Property.ValueState.Authored
        else:
            prop._value_state = Property.ValueState.NotAuthored

        for key, value in metadata.items():
            MetadataParser.set_authored(prop._metadata, key, value)

        return prop
