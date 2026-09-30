from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from .api_schema_base import APISchemaBase
from .api_wrapper import APIWrapper
from .attribute import Attribute
from .common import SchemaKind
from .dtypes import namespace
from .prim_metadata import PrimMetadata
from .prim_serializer import PrimSerializer
from .property import Property
from .relationship import Relationship
from .sdf import Specifier
from .utils import abspath, in_annotations, infer_type
from .variant_sets import VariantSets

if TYPE_CHECKING:
    from .layer import Layer


PrimType = TypeVar('PrimType')
T = TypeVar('T')

class PrimSpec:

    _name: str
    _layer: Optional[Layer]
    _metadata: PrimMetadata
    _children: Dict[str, PrimSpec]
    _parent: Optional[PrimSpec]
    _props: Dict[str, Property]
    _inherits: List[Union[PrimSpec, Layer]]
    _references: List[Union[PrimSpec, Layer]]
    _payloads: List[Union[PrimSpec, Layer]]
    _specializes: List[Union[PrimSpec, Layer]]
    _variant_sets: VariantSets
    _apis: Dict[Tuple[str, str], APISchemaBase]
    _api_wrappers: Dict[str, APIWrapper]
    _is_variant: bool = False

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped
    meta: Dict[str, Any] = {}

    _all_api_schemas: Dict[str, Type[APISchemaBase]] = {}

    def __init__(self, name:str="", specifier:Specifier=Specifier.Def)->None:
        if self.schema_kind in [SchemaKind.Invalid, SchemaKind.AbstractBase, SchemaKind.AbstractTyped]:
            raise TypeError(f"cannot instantiate abstract class {self.__class__.__name__}")

        if name == "":
            name = self.__class__.__name__

        if not name.isidentifier():
            raise ValueError(f'"{name}" is not a valid name')

        self._layer: Optional[Layer] = None
        self._name: str = name
        self._parent: Optional[PrimSpec] = None
        self._children: Dict[str, PrimSpec] = {}
        self._props: Dict[str, Property] = {}
        self._inherits: List[Union[PrimSpec, Layer]] = []
        self._references: List[Union[PrimSpec, Layer]] = []
        self._payloads: List[Union[PrimSpec, Layer]] = []
        self._specializes: List[Union[PrimSpec, Layer]] = []
        self._variant_sets: VariantSets = VariantSets(self)
        self._apis: Dict[Tuple[str, str], APISchemaBase] = {}
        self._api_wrappers: Dict[str, APIWrapper] = {}
        self._is_variant: bool = False

        inherits = []
        for base in self.__class__.__bases__:
            if not issubclass(base, PrimSpec) or base is PrimSpec:
                continue

            inherits.append(f"</{base.__name__}>")

        # A bare PrimSpec carries no typeName; every schema subclass names itself.
        type_name = "" if self.__class__ is PrimSpec else self.__class__.__name__

        self._metadata:PrimMetadata = PrimMetadata(self, {
            "specifier": specifier,
            "typeName": type_name,
            "apiSchemas": [],
            "assetInfo": {
                "identifier": None,
                "name": None,
                "payloadAssetDependencies": None,
                "version": None
            },
            "inherits": inherits,
            "references": [],
            "payloads": [],
            "specializes": [],
            "variantSets": [],
            "variants": {},
            "doc": self.__class__.__doc__
        })

    def _touch(self) -> None:
        prim = self
        while prim._layer is None and prim._parent is not None:
            prim = prim._parent
        if prim._layer is not None:
            prim._layer._touch()

    @property
    def specifier(self)->Specifier:
        return self._metadata.specifier

    @specifier.setter
    def specifier(self, specifier:Specifier)->None:
        self._metadata.specifier = specifier

    @property
    def variant_sets(self)->VariantSets:
        return self._variant_sets

    def _fetch_from_class(self, cls:Union[Type[PrimSpec], Type[APISchemaBase]], instance_name:str="")->None:
        prefix = ""
        start = self
        if instance_name:
            prefix = cls.meta["customData"]["propertyNamespacePrefix"]
            if prefix not in self._props:
                prefix_prop = self.create_prop(Property(prefix, is_leaf=False))
            else:
                prefix_prop = self._props[prefix]

            start = prefix_prop.create_prop(Property(instance_name, is_leaf=False))

        for name, value in cls.__dict__.items():
            if name == "meta":
                self._metadata.update(value)
                continue

            if not isinstance(value, Property):
                continue

            value._name = name
            if name not in start._props:
                prop = value.clone()
                prop._parent = start
                start._props[name] = prop
            else:
                prop = start._props[name]
                prop.update_children(value)

    def _declared_prop(self, name:str)->Optional[Property]:
        """Look up a property declared by this prim's type in the schema registry.

        Returns None for untyped prims and for names the type does not declare.
        """
        type_name = self._metadata._builtin_data.get("typeName") or ""
        if not type_name:
            return None

        from . import schema_registry

        declared = schema_registry.declared_prop(type_name, name)
        if declared is None:
            return None

        prop = declared.clone()
        prop._name = name.split(":")[-1]
        prop._parent = self
        prop._value_state = Property.ValueState.Fallback
        return prop

    def _install_declared(self, name:str, declared:Property)->Property:
        """Install a lazily resolved declaration, keeping any authored value."""
        parts = name.split(":")
        current = self
        for part in parts[:-1]:
            existing = current._props.get(part)
            if existing is None:
                existing = current.create_prop(
                    Property(part, custom=True, is_leaf=False)
                )

            current = existing

        leaf = parts[-1]
        authored = current._props.get(leaf)
        if authored is not None:
            return authored

        return current.create_prop(declared)

    def create_prop(self, prop:Property)->Property:
        self._props[prop.name] = prop
        prop._parent = self
        self._touch()
        return prop

    def create_attr(self, value_type:type, name:str, value:Optional[T]=None, doc:str="", metadata:Optional[Dict[str, Any]]=None, is_leaf:bool=True, uniform:bool=False, custom:bool=False, fix_type:bool=True)->Attribute[T]:
        ori_name = name
        names = name.split(":")

        current = self
        for i, name in enumerate(names):
            last = i == len(names) - 1
            if name not in current._props:
                if last:
                    attr = Attribute(value_type, name, value, doc, metadata, is_leaf, uniform, custom, fix_type)
                    if value is not None:
                        # Attribute() leaves a supplied value in the Fallback state,
                        # which is what schema declarations rely on. An initial
                        # value passed to create_attr is a real opinion.
                        attr._value_state = Property.ValueState.Authored

                    current = current.create_prop(attr)
                else:
                    current = current.create_prop(Attribute(namespace, name, is_leaf=False))
            else:
                current = current._props[name]
                if last and current._value_state > Property.ValueState.NotAuthored:
                    raise RuntimeError(f"Attribute {ori_name} already exists")
                else:
                    current._value_state = Property.ValueState.NotAuthored

        # names always has at least one entry, so the loop leaves current on the
        # leaf property; the intermediate namespace entries are plain Attributes.
        return cast(Attribute[T], current)

    def create_rel(self, name:str, doc:str="", metadata:Optional[Dict[str, Any]]=None, custom:bool=False, is_leaf:bool=True)->Relationship:
        ori_name = name
        names = name.split(":")

        current = self
        for i, name in enumerate(names):
            last = i == len(names) - 1
            if name not in current._props:
                if last:
                    current = current.create_prop(Relationship(name, doc, metadata, custom, is_leaf))
                else:
                    current = current.create_prop(Attribute(namespace, name, is_leaf=False))
            else:
                current = current._props[name]
                if last and current._value_state > Property.ValueState.NotAuthored:
                    raise RuntimeError(f"Relationship {ori_name} already exists")
                else:
                    current._value_state = Property.ValueState.NotAuthored

        # As in create_attr: the loop always ends on the leaf relationship.
        return cast(Relationship, current)

    def has_prop(self, name:str)->bool:
        names = name.split(":")
        name = names[0]

        current = self
        for part in names[1:]:
            if part not in current._props:
                return False

            current = current._props[part]

        if name in current._props:
            return True

        return self._declared_prop(name) is not None

    def prop(self, name:str)->Property:
        names = name.split(":")
        name = names[0]

        current = self
        for part in names[1:]:
            if part not in current._props:
                raise KeyError(part)

            current = current._props[part]

        if name not in current._props:
            declared = self._declared_prop(name)
            if declared is None:
                raise KeyError(name)

            return self._install_declared(name, declared)

        return current._props[name]

    def _getitem(self, path_items:List[str])->PrimSpec:
        prim = self
        for path_item in path_items:
            prim = prim._children[path_item]

        return prim

    def __getitem__(self, path:str)->PrimSpec:
        if path.startswith("/"):
            raise ValueError("path must be relative")

        path_items = path.split("/")
        return self._getitem(path_items)

    def _setitem(self, path_items:List[str], prim:PrimSpec)->None:
        name = path_items[-1]
        if not name.isidentifier():
            raise ValueError(f'"{name}" is not a valid name')

        path_items = path_items[:-1]
        parent_prim = self
        specifier = (Specifier.Def if prim.specifier != Specifier.Over else Specifier.Over)
        for path_item in path_items:
            if path_item not in parent_prim._children:
                new_prim = PrimSpec(path_item, specifier=specifier)
                new_prim._set_layer(self._layer)
                new_prim._parent = parent_prim
                parent_prim._children[path_item] = new_prim
                parent_prim = new_prim
            else:
                parent_prim = parent_prim._children[path_item]

        prim.detach_from_parent()
        prim.detach_from_layer()

        prim._parent = parent_prim
        prim._name = name
        prim._set_layer(self._layer)
        parent_prim._children[name] = prim
        self._touch()

    def __setitem__(self, path:str, prim:PrimSpec)->None:
        if path.startswith("/"):
            raise ValueError("path must be relative")

        path_items = path.split("/")
        self._setitem(path_items, prim)

    def _delitem(self, path_items:List[str])->None:
        name = path_items[-1]
        path_items = path_items[:-1]
        parent_prim = self
        for path_item in path_items:
            parent_prim = parent_prim._children[path_item]

        prim:PrimSpec = parent_prim._children[name]
        prim._parent = None
        prim._set_layer(None)
        del parent_prim._children[name]
        self._touch()

    def __delitem__(self, path:str)->None:
        if path.startswith("/"):
            raise ValueError("path must be relative")

        path_items = path.split("/")
        self._delitem(path_items)

    @property
    def prop_names(self)->List[str]:
        return list(self._props.keys())

    @property
    def props(self)->List[Property]:
        return list(self._props.values())

    def child(self, name:str)->PrimSpec:
        return self._children[name]

    @property
    def children(self)->List[PrimSpec]:
        return list(self._children.values())

    @property
    def child_names(self)->List[str]:
        return list(self._children.keys())

    def add_child(self, prim:PrimSpec)->None:
        if prim._parent is self:
            return

        prim.detach_from_parent()
        prim.detach_from_layer()

        self._children[prim.name] = prim
        prim._parent = self
        prim._set_layer(self._layer)
        self._touch()

    def def_(self, prim_type:type, path:str)->PrimSpec:
        prim = PrimSpec(specifier=Specifier.Def)
        if prim_type is not None:
            prim._metadata._builtin_data["typeName"] = prim_type.__name__

        self[path] = prim
        return prim

    def class_(self, path:str)->PrimSpec:
        prim = PrimSpec(specifier=Specifier.Class)
        self[path] = prim
        return prim

    def over_(self, path:str)->PrimSpec:
        prim = PrimSpec(specifier=Specifier.Over)
        self[path] = prim
        return prim

    def inherit(self, prim:Union[PrimSpec, Layer], prepend:bool=True)->None:
        if prim in self._inherits:
            return

        if prepend:
            self._inherits.insert(0, prim)
        else:
            self._inherits.append(prim)
        self._touch()

    def remove_inherit(self, prim:Union[PrimSpec, Layer])->None:
        if prim not in self._inherits:
            return

        self._inherits.remove(prim)
        self._touch()

    def reference(self, prim:Union[PrimSpec, Layer], prepend:bool=True)->None:
        if prim in self._references:
            return

        if prepend:
            self._references.insert(0, prim)
        else:
            self._references.append(prim)
        self._touch()

    def remove_reference(self, prim:Union[PrimSpec, Layer])->None:
        if prim not in self._references:
            return

        self._references.remove(prim)
        self._touch()

    def payload(self, prim:Union[PrimSpec, Layer], prepend:bool=True)->None:
        if prim in self._payloads:
            return

        if prepend:
            self._payloads.insert(0, prim)
        else:
            self._payloads.append(prim)
        self._touch()

    def remove_payload(self, prim:Union[PrimSpec, Layer])->None:
        if prim not in self._payloads:
            return

        self._payloads.remove(prim)
        self._touch()

    def specialize(self, prim:Union[PrimSpec, Layer], prepend:bool=True)->None:
        if prim in self._specializes:
            return

        if prepend:
            self._specializes.insert(0, prim)
        else:
            self._specializes.append(prim)
        self._touch()

    def remove_specialize(self, prim:Union[PrimSpec, Layer])->None:
        if prim not in self._specializes:
            return

        self._specializes.remove(prim)
        self._touch()

    def remove_child(self, prim:Union[str, PrimSpec])->PrimSpec:
        if isinstance(prim, str):
            if prim not in self._children:
                raise KeyError(prim)

            prim = self._children[prim]
        else:
            if prim._parent is not self:
                raise ValueError(f"{prim} is not a child of current prim")

        prim._parent = None
        prim._set_layer(None)
        del self._children[prim.name]
        return prim

    def detach_from_parent(self)->None:
        if self._parent is None:
            return

        self._parent.remove_child(self)

    def detach_from_layer(self)->None:
        if self._layer is None or self._parent is not None:
            return

        self._layer.remove_root_prim(self)

    @property
    def metadata(self)->PrimMetadata:
        return self._metadata

    @property
    def name(self)->str:
        return self._name

    @name.setter
    def name(self, name:str)->None:
        if self._name == name:
            return

        if not name.isidentifier():
            raise ValueError(f'"{name}" is not a valid name')

        old_parent = self._parent
        old_layer = self._layer
        if old_parent is None and old_layer is None:
            self._name = name
            return

        if old_parent is not None and name in old_parent._children:
            raise ValueError(f'Prim with name "{name}" already exists in parent\'s children')
        if old_parent is None and old_layer is not None and name in old_layer._root_prims:
            raise ValueError(f'Prim with name "{name}" already exists in layer\'s root prims')

        self.detach_from_parent()
        self.detach_from_layer()
        self._name = name

        if old_parent is not None:
            old_parent.add_child(self)
        elif old_layer is not None:
            old_layer.add_root_prim(self)

    @property
    def parent(self)->Optional[PrimSpec]:
        return self._parent

    @property
    def layer(self)->Optional[Layer]:
        return self._layer

    def _set_layer(self, layer:Optional[Layer])->None:
        self._layer = layer
        for child in self._children.values():
            child._set_layer(layer)

    @property
    def path(self)->str:
        path:str = self._name
        prim:PrimSpec = self
        while True:
            if prim._parent is not None:
                if not prim._parent._is_variant:
                    path = prim._parent.name + "/" + path
                prim = prim._parent
            else:
                if self.layer is not None:
                    path = "/" + path

                return path

    def id(self, rel_layer:Optional[Union[str, Layer]]=None)->str:
        prefix:str = ""
        if self.layer is not None:
            prefix = self.layer.id(rel_layer)

        return f"{prefix}<{self.path}>"

    def __hash__(self)->int:
        return id(self)

    def __eq__(self, other:Any)->bool:
        if isinstance(other, PrimSpec):
            return (self.id() == other.id())
        elif isinstance(other, str):
            return (self.id() == abspath(other))
        else:
            return False

    def __neq__(self, other:Any)->bool:
        if isinstance(other, PrimSpec):
            return (self.id() != other.id())
        elif isinstance(other, str):
            return (self.id() != abspath(other))
        else:
            return True

    @property
    def depth(self)->int:
        depth:int = 0
        prim:PrimSpec = self
        while True:
            if prim._parent is not None:
                if not prim._parent._is_variant:
                    depth += 1
                prim = prim._parent
            else:
                return depth

    @property
    def is_variant(self)->bool:
        return self._is_variant

    def __str__(self)->str:
        return self.__class__.__name__ + "(<" + self.path + ">)"

    def __getattr__(self, name:str)->Union[Property, APISchemaBase, APIWrapper]:
        if name in self._props:
            return self._props[name]

        declared = self._declared_prop(name)
        if declared is not None:
            return self._install_declared(name, declared)

        if name.endswith("_api"):
            if (name, "") in self._apis:
                return self._apis[name, ""]

            api_type = APISchemaBase.schema(name)
            if "customData" in api_type.meta and "apiSchemaCanOnlyApplyTo" in api_type.meta["customData"]:
                allowed_types = api_type.meta["customData"]["apiSchemaCanOnlyApplyTo"]

                # The prim's schema identity lives in its metadata, not in the
                # Python class: every stored spec is a plain PrimSpec and the
                # typed class only exists on the (stage, path) view. The
                # registry supplies the schema inheritance chain, so a Mesh
                # satisfies an apiSchemaCanOnlyApplyTo of Imageable.
                schema_names = {self._metadata.typeName}
                schema_names.update(inherit.strip("</>") for inherit in self._metadata.inherits)

                from . import schema_registry

                # schema_type reports direct bases only, so walk the chain.
                pending = [self._metadata.typeName]
                while pending:
                    entry = schema_registry.schema_type(pending.pop())
                    if entry is None:
                        continue

                    for base in entry.bases:
                        if base not in schema_names:
                            schema_names.add(base)
                            pending.append(base)

                if schema_names.isdisjoint(allowed_types):
                    raise ValueError(f"{api_type.__name__} cannot applied to {self._metadata.typeName}")

            if api_type.schema_kind != SchemaKind.MultipleApplyAPI:
                self._apis[name, ""] = api_type(self)
                return self._apis[name, ""]
            else:
                if name not in self._api_wrappers:
                    self._api_wrappers[name] = APIWrapper(name, api_type, self)
                return self._api_wrappers[name]

        return self.create_prop(Property(name, custom=True, is_leaf=False))

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return

        from .attribute import Attribute
        from .relationship import Relationship

        is_rel:bool = (isinstance(value, PrimSpec) or (isinstance(value, list) and len(value) > 0 and all(isinstance(item, PrimSpec) for item in value)) or isinstance(value, Relationship))
        if name in self._props:
            prop = self._props[name]
            if isinstance(prop, Attribute) and is_rel:
                if not prop._custom:
                    if isinstance(value, PrimSpec):
                        error_message = "cannot assign Prim to Attribute"
                    elif isinstance(value, list):
                        error_message = "cannot assign List[Prim] to Attribute"
                    elif isinstance(value, Relationship):
                        error_message = "cannot assign Relationship to Attribute"

                    raise TypeError(error_message)

                del self._props[name]

            if isinstance(prop, Relationship) and not is_rel:
                if not prop._custom:
                    raise TypeError(f"cannot assign {value.__class__} object to Relationship")

                del self._props[name]

        if name not in self._props and isinstance(value, Property):
            if value._parent is None:
                value._name = name
                self.create_prop(value)
            else:
                cloned_value = value.clone()
                cloned_value._name = name
                self.create_prop(cloned_value)

            return

        if name not in self._props:
            if is_rel:
                self.create_prop(Relationship(name, custom=True, is_leaf=False))
            else:
                self.create_prop(Attribute(infer_type(value), name, uniform=False, custom=True, is_leaf=False, fix_type=False))

        # One of the two branches above just installed an Attribute or a
        # Relationship; set() comes from Data on those.
        cast(Union[Attribute, Relationship], self._props[name]).set(value)
        self._touch()

    def to_str(self, indents: int = 0)->str:
        return PrimSerializer.to_str(self, indents)


    @classmethod
    def cls_to_str(cls)->str:
        return PrimSerializer.cls_to_str(cls)
