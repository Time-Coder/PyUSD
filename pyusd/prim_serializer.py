from __future__ import annotations

from typing import TYPE_CHECKING, Type

from .common import SchemaKind
from .metadata import Metadata
from .property import Property
from .sdf import Specifier

if TYPE_CHECKING:
    from .prim import Prim


class PrimSerializer:

    @staticmethod
    def to_str(prim: Prim, indents: int)->str:
        tabs = "    " * indents
        prim_type_name = prim.__class__.__name__
        if prim._is_variant:
            result = f'{tabs}"{prim.name}"'
        elif prim_type_name == "Prim" or prim.specifier != Specifier.Def:
            result = f'{tabs}{prim.specifier} "{prim.name}"'
        else:
            result = f'{tabs}{prim.specifier} {prim_type_name} "{prim.name}"'

        metadata_str = prim._metadata.to_str(indents)
        if metadata_str:
            result += (" " + metadata_str)

        result += (" " if prim._is_variant else f"\n{tabs}")
        result += '{\n'

        props_str_list = []
        for prop in prim._props.values():
            prop_str = prop.to_str(indents+1)
            if prop_str:
                props_str_list.append(prop_str)

        if props_str_list:
            result += "\n".join(props_str_list) + "\n"

        children_str_list = []
        for child in prim._children.values():
            children_str_list.append(child.to_str(indents + 1))

        for variant_set in prim._variant_sets.values():
            if not variant_set:
                continue

            children_str_list.append(variant_set.to_str(indents + 1))

        if children_str_list:
            if props_str_list:
                result += "\n"

            result += "\n".join(children_str_list)

        result += f'{tabs}}}\n'
        return result

    @staticmethod
    def cls_to_str(cls: Type[Prim])->str:
        prim_type_name = cls.__name__
        if cls.schema_kind == SchemaKind.ConcreteTyped:
            result = f'class {prim_type_name} "{prim_type_name}"'
        else:
            result = f'class "{prim_type_name}"'

        if "meta" in cls.__dict__:
            metadata = Metadata(cls, cls.meta)
        else:
            metadata = Metadata(cls)

        update_metadata = {}
        inherits = []
        for base in cls.__bases__:
            if not issubclass(base, Prim) or base == Prim:
                continue

            inherits.append(f"</{base.__name__}>")

        if inherits:
            update_metadata["inherits"] = inherits

        if cls.__doc__:
            update_metadata["doc"] = cls.__doc__

        metadata.update(update_metadata)

        metadata_str = metadata.to_str(0, True)
        if metadata_str:
            result += (" " + metadata_str)

        result += '\n{\n'

        props_str_list = []
        for name, prop in cls.__dict__.items():
            if not isinstance(prop, Property):
                continue

            prop._name = name
            prop_str = prop.to_str(1, full=True)
            if prop_str:
                props_str_list.append(prop_str)

        if props_str_list:
            result += "\n".join(props_str_list) + "\n"

        result += '}\n'
        return result
