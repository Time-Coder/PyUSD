from __future__ import annotations
from typing import TYPE_CHECKING

from .property import Property
from .dtypes import namespace
from .utils import usd_value_str

if TYPE_CHECKING:
    from .attribute import Attribute
    

class AttributeSerializer:

    @staticmethod
    def to_str(attr: Attribute, indents:int=0, full:bool=False) -> str:
        result_list = []
        full_name = attr.full_name
        if (full or attr.value_state != Property.ValueState.Fallback) and attr._type != namespace:
            tabs = "    " * indents
            prefix = ""
            if attr._custom:
                prefix += "custom "
            if attr._uniform:
                prefix += "uniform "

            line = f"{tabs}{prefix}{attr.type_name} {full_name}"
            if (
                (attr.value_state == Property.ValueState.Fallback and attr._value is not None) or
                attr.value_state in [Property.ValueState.Authored, Property.ValueState.Cleared]
            ):
                line += f" = {attr.value_str(indents)}"

            metadata_str = attr._metadata.to_str(indents, full=full)
            if metadata_str:
                line += (" " + metadata_str)

            result_list.append(line)

            if attr._time_samples:
                line = f"{tabs}{prefix}{attr.type_name} {full_name}.timeSamples = " + usd_value_str(attr._time_samples, indents)
                result_list.append(line)

        for child in attr._children.values():
            child_str = child.to_str(indents, full=full)
            if child_str:
                result_list.append(child_str)

        result = "\n".join(result_list)
        return result