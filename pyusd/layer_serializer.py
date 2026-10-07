from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layer import Layer


class LayerSerializer:

    @staticmethod
    def to_str(layer: Layer)->str:
        result = "#usda 1.0\n"

        metadata_str = layer._metadata.to_str()
        if metadata_str:
            result += metadata_str + "\n"

        result += "\n"

        prims_str_list = []
        for prim in layer._root_prims.values():
            prims_str_list.append(prim.to_str())

        result += "\n".join(prims_str_list)
        # pxr's writer ends the layer with a blank line after the last prim.
        if prims_str_list:
            result += "\n"

        return result

    @staticmethod
    def save(layer: Layer, file_name:str="")->None:
        if file_name == "":
            file_name = layer._file_name

        abs_file_name = os.path.abspath(file_name)
        dir_name = os.path.dirname(abs_file_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(abs_file_name, "w") as f:
            f.write(layer.to_str())
