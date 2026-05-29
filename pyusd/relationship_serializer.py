from __future__ import annotations

from typing import TYPE_CHECKING

from .property import Property
from .utils import usd_value_str

if TYPE_CHECKING:
    from .relationship import Relationship


class RelationshipSerializer:

    @staticmethod
    def to_str(rel:Relationship, indents:int=0, full:bool=False)->str:
        result_list = []
        if full or rel._value_state != Property.ValueState.Fallback:
            tabs = "    " * indents
            prefix = ""
            if rel._custom:
                prefix += "custom "

            line = f"{tabs}{prefix}rel {rel.full_name}"
            if rel.value_state in [Property.ValueState.Authored, Property.ValueState.Cleared]:
                line += f" = {usd_value_str(rel._targets, indents, True)}"

            metadata_str = rel._metadata.to_str(indents, full=full)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

        for child in rel._children.values():
            child_str = child.to_str(indents, full=full)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result
