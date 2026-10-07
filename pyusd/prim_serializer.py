from __future__ import annotations

from typing import TYPE_CHECKING, Type

from .common import SchemaKind
from .metadata import Metadata
from .sdf import Specifier

if TYPE_CHECKING:
    from .prim_spec import PrimSpec


class PrimSerializer:

    @staticmethod
    def to_str(prim: PrimSpec, indents: int)->str:
        tabs = "    " * indents
        prim_type_name = prim._metadata.typeName
        if prim._is_variant:
            result = f'{tabs}"{prim.name}"'
        elif not prim_type_name or prim_type_name == "Prim" or prim.specifier != Specifier.Def:
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

        children_str_list = []
        for child in prim._children.values():
            children_str_list.append(child.to_str(indents + 1))

        for variant_set in prim._variant_sets.values():
            if not variant_set:
                continue

            children_str_list.append(variant_set.to_str(indents + 1))

        if props_str_list:
            result += "\n".join(props_str_list) + "\n"

            # pxr puts a blank line between the property list and what comes
            # after it, but only when something does: a prim holding properties
            # and nothing else closes straight after the last one.
            if children_str_list:
                result += "\n"

        if children_str_list:
            # Every child string ends in a newline, so a separator of one puts
            # a blank line between siblings, both inside a variant and in the
            # prim body. The first child instead takes its blank line from the
            # property list above, since there is no sibling before it.
            for index, child_str in enumerate(children_str_list):
                if index:
                    result += "\n"
                result += child_str

        result += f'{tabs}}}\n'
        return result

    @staticmethod
    def cls_to_str(cls: Type[PrimSpec])->str:
        from . import schema_registry

        prim_type_name = cls.__name__
        if cls.schema_kind == SchemaKind.ConcreteTyped:
            result = f'class {prim_type_name} "{prim_type_name}"'
        else:
            result = f'class "{prim_type_name}"'

        metadata = Metadata(cls, cls.meta) if "meta" in cls.__dict__ else Metadata(cls)

        update_metadata = {}
        inherits = []
        for base in cls.__bases__:
            if not issubclass(base, PrimSpec) or base == PrimSpec:
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

        # Declarations live in the schema registry rather than on the class, so
        # they can be dropped from the class without losing the schema definition.
        entry = schema_registry.schema_type(prim_type_name)
        declared = entry.declared_props if entry is not None else {}

        props_str_list = []
        for name, prop in declared.items():
            prop = prop.clone()
            prop._name = name
            prop_str = prop.to_str(1, full=True)
            if prop_str:
                props_str_list.append(prop_str)

        if props_str_list:
            result += "\n".join(props_str_list) + "\n"

        result += '}\n'
        return result
