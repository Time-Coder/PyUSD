from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any, List, Optional

from .usda_serializer import UsdaSerializer
from .utils import infer_type

if TYPE_CHECKING:
    from .layer import Layer
    from .metadata import Metadata


class MetadataSerializer:

    _ASSET_ARC_RE = re.compile(r"^@([^@]*)@(.*)$", re.DOTALL)

    @staticmethod
    def _rebase_cwd_relative_assets(values: Any, rel_layer: Optional[Layer]) -> Any:
        """Re-express marked asset paths against the directory this layer is written to.

        An asset path authored while its layer had no file name was resolved against the
        working directory, and a relative path is otherwise read relative to the layer
        holding it -- so the same string denotes a different file once the layer has an
        address. Only paths Prim._note_cwd_relative_asset marked are touched, which is
        what keeps a relative path that came out of a file byte for byte unchanged; the
        alternative, rebasing every relative path, makes a round trip depend on where the
        script was run from.

        The comparison is on resolved paths rather than on spelling, so a marked path that
        already means the right file is left alone.
        """
        if rel_layer is None or not rel_layer.file_name:
            return values

        pending = getattr(rel_layer._impl, "_cwd_relative_assets", None)
        if not pending:
            return values

        anchor_dir = os.path.dirname(os.path.abspath(rel_layer.file_name))

        def rebase(value: Any) -> Any:
            if not isinstance(value, str):
                return value

            match = MetadataSerializer._ASSET_ARC_RE.match(value.strip())
            if match is None:
                return value

            asset, tail = match.group(1), match.group(2)
            if asset not in pending or os.path.isabs(asset):
                return value

            # What the author meant: the path resolved against the working directory.
            as_authored = os.path.normcase(os.path.abspath(asset))
            # What the stored string will mean once it is read back, since a relative
            # path is read relative to the layer holding it. Comparing the rebased form
            # against the authored one would be circular -- relpath is computed to make
            # those equal -- so it is the as-read meaning that has to match.
            as_stored = os.path.abspath(os.path.join(anchor_dir, asset))
            if os.path.normcase(as_stored) == as_authored:
                return value

            # Both spellings are relative and neither is wrong on its face: "./a.usda"
            # beside the layer and "./a.usda" beside the script are different files and the
            # string cannot say which was meant. The filesystem can. If the as-stored
            # reading already resolves, it is the one the author wrote against and is left
            # alone; otherwise the authored reading is re-expressed, and if neither
            # resolves nothing is guessed.
            if os.path.exists(as_stored):
                return value
            if not os.path.exists(as_authored):
                return value

            rebased = os.path.relpath(as_authored, anchor_dir).replace(os.sep, "/")
            return f"@{rebased}@{tail}"

        if isinstance(values, list):
            return [rebase(item) for item in values]

        return rebase(values)

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

            if is_ref:
                value = MetadataSerializer._rebase_cwd_relative_assets(value, rel_layer)

            value_str = UsdaSerializer.value_str(
                value, indents+1,
                degenerate_list=(is_ref and key != "subLayers"),
                rel_layer=rel_layer,
                need_quote=(not is_ref or key in ["variantSets", "variants"])
            )
            if is_ref and key not in ["subLayers", "variants", "relocates"]:
                # USD's field is `payload`, singular. Writing `payloads` produces a file
                # OpenUSD will not open -- it reads the list-op prefix and then expects
                # None or a bracket, not an asset path. The builtin key stays `payloads`
                # because that is the name this package exposes on prim.metadata; only
                # the file gets the spelling USD understands.
                out_key = "payload" if key == "payloads" else key
                builtin_str_list.append(f"{next_tabs}prepend {out_key} = {value_str}")
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
