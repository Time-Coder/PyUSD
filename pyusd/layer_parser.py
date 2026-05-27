from __future__ import annotations
from typing import TYPE_CHECKING
from tree_sitter import Parser, Language
import tree_sitter_usd

from .usda_parser import UsdaParser
from .prim_parser import PrimParser
from .metadata_parser import MetadataParser

if TYPE_CHECKING:
    from .layer import Layer


class LayerParser:

    @staticmethod
    def load(file_name:str) -> Layer:
        from .layer import Layer
        
        layer = Layer(file_name)

        with open(file_name, "rb") as f:
            code = f.read()

        parser = Parser(Language(tree_sitter_usd.language()))
        tree = parser.parse(code)

        pending_default_prim = None
        for child in tree.root_node.named_children:
            if child.type == "metadata":
                metadata = UsdaParser.load_metadata_assignments(child)
                pending_default_prim = metadata.pop("defaultPrim", pending_default_prim)
                sub_layers = metadata.pop("subLayers", None)
                if sub_layers is not None:
                    layer._sub_layers = [
                        Layer(UsdaParser.resolve_asset_path(str(item).strip("@")))
                        for item in UsdaParser.as_list(sub_layers)
                    ]
                    layer._metadata._builtin_is_set["subLayers"] = True

                for key, value in metadata.items():
                    MetadataParser.set_authored(layer._metadata, key, value)
            elif child.type == "prim_definition":
                layer.add_root_prim(PrimParser.parse(child))

        if pending_default_prim:
            layer._default_prim = layer._root_prims.get(str(pending_default_prim))
            MetadataParser.set_authored(layer._metadata, "defaultPrim", pending_default_prim)
    
        return layer