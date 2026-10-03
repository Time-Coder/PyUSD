from __future__ import annotations

from typing import TYPE_CHECKING

from .property_spec import PropertySpec
from .usda_serializer import UsdaSerializer

if TYPE_CHECKING:
    from .relationship_spec import RelationshipSpec


class RelationshipSerializer:

    @staticmethod
    def to_str(rel:RelationshipSpec, indents:int=0, full:bool=False)->str:
        result_list = []
        if full or rel._value_state != PropertySpec.ValueState.Fallback:
            tabs = "    " * indents
            prefix = ""
            if rel._custom:
                prefix += "custom "

            line = f"{tabs}{prefix}rel {rel.full_name}"
            if rel.value_state in [PropertySpec.ValueState.Authored, PropertySpec.ValueState.Cleared]:
                line += f" = {UsdaSerializer.value_str(rel._targets, indents, True, need_quote=False)}"

            metadata_str = rel._metadata.to_str(indents, full=full)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

        for child in rel._props.values():
            child_str = child.to_str(indents, full=full)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result
