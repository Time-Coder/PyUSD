from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, Optional, Union, cast

from .common import SchemaKind
from .metadata import Metadata
from .property_serializer import PropertySerializer
from .utils import in_annotations, infer_type

if TYPE_CHECKING:
    from .api_schema_base import APISchemaBase
    from .attribute import Attribute
    from .prim_spec import PrimSpec
    from .relationship import Relationship

# Fields Property.clone manages itself; anything else on a subclass instance is
# state the clone has to carry over.
_CLONE_MANAGED_FIELDS = frozenset(
    {"_parent", "_name", "_metadata", "_props", "_custom", "_is_leaf", "_value_state"}
)


class Property:

    class ValueState(IntEnum):
        Fallback = 0
        NotAuthored = 1
        Authored = 2
        Cleared = 3

    # Any rather than Union[PrimSpec, Property]: a self-referential annotation in
    # this class body makes type checkers treat the attribute as read-only, which
    # breaks the legitimate `prop._parent = prim` assignments below. Metadata
    # declares its own `_parent` as Any for the same reason.
    _parent: Any
    _name: str
    _metadata: Metadata
    _props: Dict[str, Property]
    _is_leaf: bool
    _custom: bool
    _value_state: Property.ValueState

    meta: Dict[str, Any] = {}

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

        self._parent: Optional[Union[PrimSpec, Property]] = None
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
        result._metadata._parent = result
        result._props = {}
        result._custom = self._custom
        result._is_leaf = self._is_leaf
        result._value_state = self._value_state

        # Reclassing never runs the subclass __init__, so anything a subclass
        # stored beyond the Property/Attribute contract is carried over here.
        # Subclass clones (Attribute.clone) still overwrite the fields they own.
        for key, value in self.__dict__.items():
            if key in _CLONE_MANAGED_FIELDS or key in result.__dict__:
                continue

            result.__dict__[key] = value

        if clone_child:
            for name, child in self._props.items():
                result._props[name] = child.clone()
                result._props[name]._parent = result

        return result

    def _touch(self) -> None:
        if self._parent is not None and hasattr(self._parent, "_touch"):
            self._parent._touch()

    @property
    def parent(self)->Optional[Union[PrimSpec, Property]]:
        return self._parent

    @property
    def is_leaf(self)->bool:
        return self._is_leaf

    @property
    def name(self)->str:
        return self._name

    @property
    def full_name(self)->str:
        from .prim_spec import PrimSpec

        if self._parent is None or isinstance(self._parent, PrimSpec):
            return self._name

        return self._parent.full_name + ":" + self._name

    @property
    def path(self)->str:
        if self._parent is None:
            return self.full_name

        # The parent chain already carries the namespace prefix, so the leaf name
        # is appended here; using full_name would repeat it at every level.
        return self._parent.path + "." + self._name

    @property
    def metadata(self)->Metadata:
        return self._metadata

    @property
    def value_state(self)->Property.ValueState:
        return self._value_state

    @property
    def custom(self)->bool:
        return self._custom

    def rel(self, prim:PrimSpec)->Relationship:
        if self.__class__.__name__ != "Property":
            raise AttributeError(f"'{self.__class__.__name__}' object has not attribute 'rel'")

        from .relationship import Relationship
        self.__class__ = Relationship
        self._targets = [prim]
        self._value_state = Property.ValueState.Authored
        return cast(Relationship, self)

    def create(self, value_type:type, value:Optional[Any]=None, uniform:bool=False, custom:bool=False, fix_type:bool=True)->Attribute:
        if self.__class__.__name__ != "Property":
            raise AttributeError(f"'{self.__class__.__name__}' object has not attribute 'create'")

        from .attribute import Attribute
        self.__class__ = Attribute
        self._custom = custom
        # The __class__ swap above already made this an Attribute; the cast just
        # lets the type checker see that before _init's Self-typed call.
        attribute = cast(Attribute, self)
        attribute._init(value_type, value=value, uniform=uniform, fix_type=fix_type)
        self._value_state = Property.ValueState.NotAuthored
        return attribute

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

    def __get__(self, instance:Union[PrimSpec, Property, APISchemaBase], owner)->Property:
        from .api_schema_base import APISchemaBase
        from .prim_spec import PrimSpec

        if isinstance(instance, (PrimSpec, Property)):
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
        from .prim_spec import PrimSpec

        if isinstance(instance, (PrimSpec, Property)):
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
        from .prim_spec import PrimSpec
        from .relationship import Relationship

        is_rel:bool = (isinstance(value, PrimSpec) or (isinstance(value, list) and all(isinstance(item, PrimSpec) for item in value)) or isinstance(value, Relationship))
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

        if name not in self._props and self._is_leaf:
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
            if not isinstance(value, PrimSpec):
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
                # A PrimSpec target means a new relationship, and there is no
                # source Property here to inherit flags from, so it is custom.
                self.create_prop(Relationship(name, custom=True, is_leaf=False))

        # Both branches above leave an Attribute or a Relationship in place, and
        # set() comes from Data on those; the dict itself is typed as Property.
        prop = cast(Union[Attribute, Relationship], self._props[name])
        prop.set(value)

    def to_str(self, indents:int=0, full:bool=False)->str:
        return PropertySerializer.to_str(self, indents, full)
