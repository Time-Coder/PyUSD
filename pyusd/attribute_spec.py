from __future__ import annotations

import copy
from typing import Any, Dict, Iterable, Optional, TypeVar, cast

from .attribute_serializer import AttributeSerializer
from .data import Data
from .dtypes import token
from .property_spec import PropertySpec
from .utils import in_annotations

T = TypeVar('T')
class AttributeSpec(PropertySpec, Data[T]):

    _time_samples: Dict[float, T]
    _uniform: bool
    _fix_type: bool

    def __init__(self, value_type:type, name:str="", value:Any=None, doc:str="", metadata:Optional[Dict[str, Any]]=None, is_leaf:bool=True, uniform:bool=False, custom:bool=False, fix_type:bool=True)->None:
        if metadata is None:
            metadata = {}

        if isinstance(value_type, type) and issubclass(value_type, token) and value_type != token:
            # The allowedTokens enumerations are generated as `class X(token, ReprEnum)`,
            # so their members are Enums whose value is the token string. The guard above
            # is what separates them from token itself, which is a plain str subclass
            # and therefore not iterable.
            members: Iterable[Any] = cast(Iterable[Any], value_type)
            metadata["allowedTokens"] = [member.value for member in members]

        PropertySpec.__init__(self, name, doc=doc, metadata=metadata, custom=custom, is_leaf=is_leaf)
        self._init(value_type, value, uniform, fix_type)

    def _init(self, value_type:type, value:Optional[T]=None, uniform:bool=False, fix_type:bool=True)->None:
        Data.__init__(self, value_type, value)
        self._time_samples:Dict[float, T] = {}
        self._uniform:bool = uniform
        self._fix_type:bool = fix_type

    def clone(self, clone_child:bool=True)->AttributeSpec[T]:
        result = PropertySpec.clone(self, clone_child)
        result._type = self._type
        result._dtype = self._dtype
        result._array_dim = self._array_dim
        result._value = copy.deepcopy(self._value)
        result._time_samples = copy.deepcopy(self._time_samples)
        result._uniform = self._uniform
        result._fix_type = self._fix_type
        return cast(AttributeSpec[T], result)

    @property
    def timeSamples(self)->Dict[float, T]:
        return self._time_samples

    @property
    def value(self)->Optional[T]:
        return self._value

    @value.setter
    def value(self, value:Optional[T])->None:
        if value is self:
            return

        self._value = self._convert_from(value)
        self._value_state = AttributeSpec.ValueState.Authored
        self._touch()

    def clear(self)->None:
        self._value = None
        self._value_state = AttributeSpec.ValueState.Cleared
        self._touch()

    @property
    def value_state(self)->AttributeSpec.ValueState:
        # A non-empty list is treated as authored. That heuristic is about a
        # materialised spec whose value arrived without going through the setter --
        # parsing, not authoring -- and it has to stop at a spec with no parent. A
        # schema declaration has none: it is never installed in a prim, so no layer
        # holds an opinion about it, and composition hands it straight back as a
        # fallback. Without this, a declaration carrying a list default such as
        # Sphere's extent reported Authored while pxr reports HasAuthoredValue False.
        if (
            self._parent is not None
            and self._value_state != AttributeSpec.ValueState.Authored
            and isinstance(self._value, list)
            and self._value
        ):
            return AttributeSpec.ValueState.Authored

        return self._value_state

    @property
    def uniform(self)->bool:
        return self._uniform

    @uniform.setter
    def uniform(self, flag:bool)->None:
        self._uniform = flag
        self._touch()

    def __getattr__(self, name:str)->Any:
        if "_props" not in self.__dict__ or "_value" not in self.__dict__:
            return PropertySpec.__getattr__(self, name)

        if name in self._props:
            return self._props[name]
        elif hasattr(self._value, name):
            return getattr(self._value, name)
        else:
            return PropertySpec.__getattr__(self, name)

    def __setattr__(self, name:str, value:Any)->None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return

        if "_props" not in self.__dict__ or "_value" not in self.__dict__:
            return PropertySpec.__setattr__(self, name, value)

        if name in self._props:
            return PropertySpec.__setattr__(self, name, value)
        elif hasattr(self._value, name):
            return setattr(self._value, name, value)
        else:
            return PropertySpec.__setattr__(self, name, value)

    def to_str(self, indents:int=0, full:bool=False) -> str:
        return AttributeSerializer.to_str(self, indents, full)
