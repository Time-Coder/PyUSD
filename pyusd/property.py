from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from typeguard import typechecked

from .common import SchemaKind
from .metadata import Metadata
from .property_serializer import PropertySerializer
from .utils import in_annotations, infer_type

if TYPE_CHECKING:
    from .api_schema_base import APISchemaBase
    from .attribute import Attribute
    from .prim import Prim
    from .relationship import Relationship


class Property:

    class ValueState(IntEnum):
        Fallback = 0
        NotAuthored = 1
        Authored = 2
        Cleared = 3

    _parent: Optional[Union[Prim, Property]]
    _name: str
    _metadata: Metadata
    _props: Dict[str, Property]
    _is_leaf: bool
    _custom: bool
    _value_state: Property.ValueState

    meta: Dict[str, Any] = {}

    @typechecked
    def __init__(self, name:str="", doc:str="", metadata:Optional[Dict[str, Any]]=None, custom:bool=False, is_leaf:bool=True)->None:
        if metadata is None:
            metadata = {}

        if "doc" in metadata:
            doc = metadata["doc"]

        if doc == "" and self.__class__.__doc__ is not None:
            doc = self.__class__.__doc__

        if "doc" not in metadata:
            metadata["doc"] = doc

        self.__doc__ = doc

        self._parent: Optional[Union[Prim, Property]] = None
        self._name:str = name
        self._metadata:Metadata = Metadata(self, metadata)
        self._props:Dict[str, Property] = {}
        self._custom:bool = custom
        self._is_leaf:bool = is_leaf
        self._value_state:Property.ValueState = Property.ValueState.Fallback

        for klass in self.__class__.__mro__:
            if klass is object:
                continue

            for name, value in klass.__dict__.items():
                if not isinstance(value, Property):
                    continue

                value._name = name

                if name in self._props:
                    continue

                prop = value.clone()
                prop._parent = self
                self._props[name] = prop

        self._metadata.update(self.meta)

    def clone(self, clone_child:bool=True)->Property:
        result = Property()
        result.__class__ = self.__class__
        result.__doc__ = self.__doc__
        result._parent = None
        result._name = self._name
        result._metadata = self._metadata.clone()
        result._props = {}
        result._custom = self._custom
        result._is_leaf = self._is_leaf
        result._value_state = self._value_state
        if clone_child:
            for name, child in self._props.items():
                result._props[name] = child.clone()
                result._props[name]._parent = result

        return result

    @property
    def parent(self)->Optional[Union[Prim, Property]]:
        return self._parent

    @property
    def is_leaf(self)->bool:
        return self._is_leaf

    @property
    def name(self)->str:
        return self._name

    @property
    def full_name(self)->str:
        from .prim import Prim

        if self._parent is None or isinstance(self._parent, Prim):
            return self._name

        return self._parent.full_name + ":" + self._name

    @property
    def path(self)->str:
        if self._parent is None:
            return self.full_name

        return self._parent.path + "." + self.full_name

    @property
    def metadata(self)->Metadata:
        return self._metadata

    @property
    def value_state(self)->Property.ValueState:
        return self._value_state

    @property
    def custom(self)->bool:
        return self._custom

    def rel(self, prim:Prim)->Relationship:
        if self.__class__.__name__ != "Property":
            raise AttributeError(f"'{self.__class__.__name__}' object has not attribute 'rel'")

        from .relationship import Relationship
        self.__class__ = Relationship
        self._targets = [prim]
        self._value_state = Property.ValueState.Authored
        return self

    def create(self, value_type:type, value:Optional[Any]=None, uniform:bool=False, custom:bool=False, fix_type:bool=True)->Attribute:
        if self.__class__.__name__ != "Property":
            raise AttributeError(f"'{self.__class__.__name__}' object has not attribute 'create'")

        from .attribute import Attribute
        self.__class__ = Attribute
        self._custom = custom
        Attribute._init(self, value_type, value=value, uniform=uniform, fix_type=fix_type)
        self._value_state = Property.ValueState.NotAuthored
        return self

    def create_prop(self, prop:Property)->Property:
        self._props[prop.name] = prop
        prop._parent = self
        return prop

    def update_children(self, prop:Property)->None:
        for child_name, child in prop._props.items():
            if child_name not in self._props:
                self._props[child_name] = child.clone()
                self._props[child_name]._parent = self
            else:
                self._props[child_name].update_children(child)

    def __get__(self, instance:Union[Prim, Property, APISchemaBase], owner)->Property:
        from .api_schema_base import APISchemaBase
        from .prim import Prim

        if isinstance(instance, Prim):
            return instance._props[self._name]
        elif isinstance(instance, Property):
            return instance._props[self._name]
        elif isinstance(instance, APISchemaBase):
            if instance.schema_kind == SchemaKind.MultipleApplyAPI:
                prefix_prop = instance._prim._props[instance._namespace_prefix]
                start_prop = prefix_prop._props[instance._instance_name]
                return start_prop._props[self._name]
            else:
                return instance._prim._props[self._name]

    def __set__(self, instance, value:Any):
        from .api_schema_base import APISchemaBase
        from .prim import Prim

        if isinstance(instance, Prim):
            instance._props[self._name].set(value)
        elif isinstance(instance, Property):
            instance._props[self._name].set(value)
        elif isinstance(instance, APISchemaBase):
            if instance.schema_kind == SchemaKind.MultipleApplyAPI:
                prefix_prop = instance._prim._props[instance._namespace_prefix]
                start_prop = prefix_prop._props[instance._instance_name]
                start_prop._props[self._name].set(value)
            else:
                instance._prim._props[self._name].set(value)

    def __getattr__(self, name:str)->Property:
        if name not in self._props:
            self.create_prop(Property(name, custom=True, is_leaf=False))

        return self._props[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return

        from .attribute import Attribute
        from .prim import Prim
        from .relationship import Relationship

        is_rel:bool = (isinstance(value, Prim) or (isinstance(value, list) and all(isinstance(item, Prim) for item in value)) or isinstance(value, Relationship))
        if name in self._props:
            prop = self._props[name]
            if isinstance(prop, Attribute) and is_rel:
                if not prop._custom:
                    if isinstance(value, Prim):
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

        if name not in self._props:
            if self._is_leaf:
                raise AttributeError("leaf Property cannot create child Property")

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
            if not isinstance(value, Prim):
                if isinstance(self, Attribute):
                    target_type = self._type
                    target_uniform = self._uniform
                    target_custom = self._custom
                    target_fix_type = self._fix_type
                else:
                    target_type = infer_type(value)
                    target_uniform = False
                    target_custom = True
                    target_fix_type = False

                self.create_prop(Attribute(target_type, name, uniform=target_uniform, custom=target_custom, is_leaf=(not target_custom), fix_type=target_fix_type))
            else:
                self.create_prop(Relationship(name, custom=target_custom, is_leaf=False))

        self._props[name].set(value)

    def to_str(self, indents:int=0, full:bool=False)->str:
        return PropertySerializer.to_str(self, indents, full)
