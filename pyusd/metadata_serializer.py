from __future__ import annotations

from typing import TYPE_CHECKING, List

from .usda_serializer import UsdaSerializer
from .utils import infer_type

if TYPE_CHECKING:
    from .metadata import Metadata


class MetadataSerializer:

    @staticmethod
    def _dedupe(values):
        """Order-preserving de-duplication for composed arc lists.

        The authored list and the programmatic list are two views of the same arcs,
        so merging them must not repeat an entry on every serialize round trip.
        """
        seen = set()
        result = []
        for value in values:
            key = id(value) if not isinstance(value, (str, int, float, bool, tuple)) else value
            if key in seen:
                continue

            seen.add(key)
            result.append(value)

        return result

    @staticmethod
    def to_str(metadata:Metadata, indents:int=0, full:bool=False)->str:
        from .layer import Layer
        from .prim_spec import PrimSpec

        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)
        next2_tabs = "    " * (indents + 2)
        result = "(\n"

        builtin_str_list:List[str] = []
        for key, value in metadata._builtin_data.items():
            is_ref = key in ["inherits", "references", "payloads", "specializes", "subLayers", "relocates", "variantSets", "variants"]
            use_ori_value = True
            ori_value = value
            if not full and not metadata._builtin_is_set[key]:
                if not is_ref:
                    continue
                use_ori_value = False

            if value is None:
                continue

            if key == "doc" and isinstance(value, str) and value == "":
                continue

            if key == "inherits":
                # Inherits are always local paths, never asset references.
                value = [
                    f"<{item.path}>" if not isinstance(item, str) else item
                    for item in metadata._parent._inherits
                ]
            elif key == "references":
                value = metadata._parent._references
            elif key == "payloads":
                value = metadata._parent._payloads
            elif key == "specializes":
                value = metadata._parent._specializes
            elif key == "relocates":
                value = metadata._parent._relocates
            elif key == "variantSets":
                value = list(metadata._parent._variant_sets.keys())
            elif key == "variants":
                value = {}
                for variant_set in metadata._parent._variant_sets.values():
                    selected_variant = variant_set._selected_variant
                    if selected_variant is None:
                        continue

                    value[variant_set._name] = selected_variant._name
            elif key == "subLayers":
                value = metadata._parent._sub_layers

            if is_ref and use_ori_value:
                if isinstance(value, dict) and isinstance(ori_value, dict):
                    value.update(ori_value)
                else:
                    value += ori_value
                    value = MetadataSerializer._dedupe(value)

            if is_ref and not value:
                continue

            rel_layer = None
            if metadata._parent is not None:
                if isinstance(metadata._parent, PrimSpec) and metadata._parent.layer is not None:
                    rel_layer = metadata._parent.layer
                elif isinstance(metadata._parent, Layer):
                    rel_layer = metadata._parent

            value_str = UsdaSerializer.value_str(
                value, indents+1,
                degenerate_list=(is_ref and key != "subLayers"),
                rel_layer=rel_layer,
                need_quote=(not is_ref or key in ["variantSets", "variants"])
            )
            if is_ref and key not in ["subLayers", "variants", "relocates"]:
                builtin_str_list.append(f"{next_tabs}prepend {key} = {value_str}")
            else:
                builtin_str_list.append(f"{next_tabs}{key} = {value_str}")

        custom_str_list:List[str] = []
        for key, value in metadata._custom_data.items():
            if not full and not metadata._custom_is_set[key]:
                continue

            if value is None:
                continue

            custom_str_list.append(f"{next2_tabs}{UsdaSerializer.type_str(infer_type(value))} {key} = {UsdaSerializer.value_str(value, indents+2)}")

        if len(builtin_str_list) == 0 and len(custom_str_list) == 0:
            return ""

        if builtin_str_list:
            result += "\n".join(builtin_str_list) + "\n"

        if custom_str_list:
            result += f"{next_tabs}customData = {{\n"
            result += "\n".join(custom_str_list)
            result += f"\n{next_tabs}}}\n"

        result += f"{tabs})"

        return result
