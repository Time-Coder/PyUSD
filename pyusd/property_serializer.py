from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .property_spec import PropertySpec


class PropertySerializer:

    @staticmethod
    def to_str(prop: PropertySpec, indents:int=0, full:bool=False)->str:
        result_list = []
        for child in prop._props.values():
            child_str = child.to_str(indents, full=full)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result
