from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .variant_set_spec import VariantSetSpec


class VariantSetSerializer:

    @staticmethod
    def to_str(variant_set:VariantSetSpec, indents:int=0)->str:
        tabs = "    " * indents
        result = f'{tabs}variantSet "{variant_set._name}" = {{'

        if variant_set._variants:
            variant_str_list = []
            for variant in variant_set._variants.values():
                variant_str_list.append(variant.to_str(indents + 1))

            # Each variant string ends in a newline, so joining with one more
            # leaves a single blank line between two variants.
            result += "\n" + '\n'.join(variant_str_list)

        result += f"{tabs}}}\n"

        return result
