from __future__ import annotations

import os
import uuid
from typing import Any, ClassVar, Dict, List, Optional, Type, Union
from weakref import WeakValueDictionary

from beartype import beartype

from .common import Axis
from .layer_metadata import LayerMetadata
from .layer_parser import LayerParser
from .layer_serializer import LayerSerializer
from .prim import PrimSpec, PrimType
from .sdf import Specifier
from .utils import in_annotations


class LayerImpl:

    global_revision = 0

    def __init__(self, file_name: str = "") -> None:
        self._file_name: str = file_name
        self._identifier: str = f"anon:{uuid.uuid4().hex}"
        self._root_prims: Dict[str, PrimSpec] = {}
        self._default_prim: Optional[PrimSpec] = None
        self._sub_layers: List[Layer] = []
        self._relocates: Dict[str, str] = {}
        self._metadata: LayerMetadata = LayerMetadata(None, {
            "subLayers": [],
            "relocates": {},
            "defaultPrim": None,
            "endTimeCode": None,
            "metersPerUnit": 1,
            "startTimeCode": 0,
            "timeCodesPerSecond": 60,
            "upAxis": Axis.Y
        })
        self._revision = 0
        self._loaded = False
        self._dirty = False

    def touch(self) -> None:
        self._revision += 1
        self._dirty = True
        LayerImpl.global_revision += 1


class Layer:

    _registry: ClassVar[WeakValueDictionary[str, LayerImpl]] = WeakValueDictionary()
    _impl: LayerImpl
    _file_name: str
    _identifier: str
    _root_prims: Dict[str, PrimSpec]
    _default_prim: Optional[PrimSpec]
    _sub_layers: List[Layer]
    _relocates: Dict[str, str]
    _metadata: LayerMetadata
    _revision: int
    _loaded: bool
    _dirty: bool

    def __init__(self, file_name: str = "", _impl: Optional[LayerImpl] = None) -> None:
        if _impl is None:
            key = self._registry_key(file_name)
            _impl = self._registry.get(key) if key else None
            if _impl is None:
                _impl = LayerImpl(file_name)
                if key:
                    self._registry[key] = _impl

        object.__setattr__(self, "_impl", _impl)
        self._impl._metadata._parent = self

    def __getattr__(self, name: str) -> Any:
        if name != "_impl" and in_annotations(name, self.__class__):
            return getattr(self._impl, name)

        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_impl":
            object.__setattr__(self, name, value)
        elif name != "_registry" and in_annotations(name, self.__class__) and "_impl" in self.__dict__:
            setattr(self._impl, name, value)
        else:
            object.__setattr__(self, name, value)

    @staticmethod
    def _registry_key(file_name: str, anchor_file: str = "") -> str:
        if not file_name:
            return ""

        file_name = str(file_name).strip("@")
        if not os.path.isabs(file_name):
            base_dir = os.path.dirname(os.path.abspath(anchor_file)) if anchor_file else os.getcwd()
            file_name = os.path.join(base_dir, file_name)

        return os.path.normcase(os.path.abspath(file_name)).replace("\\", "/")

    @classmethod
    def _from_impl(cls, impl: LayerImpl) -> Layer:
        return cls(_impl=impl)

    @classmethod
    def _lookup(cls, file_name: str, anchor_file: str = "") -> Optional[Layer]:
        key = cls._registry_key(file_name, anchor_file)
        impl = cls._registry.get(key) if key else None
        return cls._from_impl(impl) if impl is not None else None

    @property
    def revision(self) -> int:
        return self._impl._revision

    def _touch(self) -> None:
        self._impl.touch()

    @staticmethod
    def load(file_name:str)->Layer:
        return LayerParser.load(file_name)

    def relocate(self, prim:PrimSpec, new_path:str)->None:
        self._relocates[prim] = f"<{new_path}>"
        self._touch()

    def remove_relacate(self, prim:PrimSpec)->None:
        del self._relocates[prim]
        self._touch()

    @property
    def file_name(self)->str:
        return self._file_name

    @property
    def metadata(self)->LayerMetadata:
        return self._metadata

    @property
    def default_prim(self)->PrimSpec:
        return self._default_prim

    @default_prim.setter
    @beartype
    def default_prim(self, prim:PrimSpec)->None:
        if prim.layer is None or prim.layer._impl is not self._impl:
            raise ValueError("Prim is not in current layer")

        if prim.depth != 0:
            raise ValueError("Default prim must be a root prim")

        self._default_prim = prim
        self.metadata.defaultPrim = prim.name
        self._touch()

    def id(self, rel_layer:Optional[Union[str, Layer]]=None)->str:
        if not self._file_name:
            return f"@{self._identifier}@"

        result:str = "@" + os.path.abspath(self._file_name).replace("\\", "/") + "@"
        if isinstance(rel_layer, Layer):
            rel_layer = rel_layer.file_name

        if rel_layer:
            abs_path = os.path.abspath(rel_layer).replace("\\", "/")
            self_layer_abs_path = os.path.abspath(self.file_name).replace("\\", "/")
            if abs_path != self_layer_abs_path:
                abs_folder = os.path.dirname(abs_path)
                rel_path = os.path.relpath(self_layer_abs_path, abs_folder).replace("\\", "/")
                result = f"@./{rel_path}@"

        return result

    def __eq__(self, other:Any)->bool:
        if isinstance(other, Layer):
            return (self.id() == other.id())
        elif isinstance(other, str):
            return (self.id().strip("@") == os.path.abspath(other.strip("@")).replace("\\", "/"))
        else:
            return False

    def __neq__(self, other:Any)->bool:
        if isinstance(other, Layer):
            return (self.id() != other.id())
        elif isinstance(other, str):
            return (self.id().strip("@") != os.path.abspath(other.strip("@")).replace("\\", "/"))
        else:
            return True

    @beartype
    def include(self, layer:Layer, prepend:bool=True)->None:
        if layer in self._sub_layers:
            return

        if prepend:
            self._sub_layers.insert(0, layer)
        else:
            self._sub_layers.append(layer)
        self._touch()

    @beartype
    def remove_include(self, layer:Layer)->None:
        if layer not in self._sub_layers:
            return

        self._sub_layers.remove(layer)
        self._touch()

    def __getitem__(self, path:str)->PrimSpec:
        path_items = path[1:].split("/") if path.startswith("/") else path.split("/")

        root_name = path_items[0]
        path_items = path_items[1:]
        root_prim = self._root_prims[root_name]
        return root_prim._getitem(path_items)

    def __setitem__(self, path:str, prim:PrimSpec)->None:
        path_items = path[1:].split("/") if path.startswith("/") else path.split("/")

        root_name = path_items[0]
        if len(path_items) == 1:
            prim.detach_from_parent()
            prim.detach_from_layer()

            prim._name = root_name
            prim._set_layer(self)
            self._root_prims[root_name] = prim
            self._touch()
            return

        path_items = path_items[1:]
        specifier = (Specifier.Def if prim.specifier != Specifier.Over else Specifier.Over)
        if root_name not in self._root_prims:
            parent_prim = PrimSpec(root_name, specifier=specifier)
            parent_prim._set_layer(self)
            self._root_prims[root_name] = parent_prim
        parent_prim = self._root_prims[root_name]
        parent_prim._setitem(path_items, prim)
        self._touch()

    def __delitem__(self, path:str)->None:
        path_items = path[1:].split("/") if path.startswith("/") else path.split("/")

        root_name = path_items[0]
        if len(path_items) == 1:
            if root_name not in self._root_prims:
                raise KeyError(root_name)

            prim:PrimSpec = self._root_prims[root_name]
            prim._set_layer(None)
            del self._root_prims[root_name]
            self._touch()
            return

        path_items = path_items[1:]
        parent_prim = self._root_prims[root_name]
        parent_prim._delitem(path_items)
        self._touch()

    def add_root_prim(self, prim:PrimSpec)->None:
        if prim._parent is None and prim._layer is self:
            return

        prim.detach_from_parent()
        prim.detach_from_layer()

        self._root_prims[prim.name] = prim
        prim._set_layer(self)
        self._touch()

    def remove_root_prim(self, prim:Union[str, PrimSpec])->PrimSpec:
        if isinstance(prim, str):
            if prim not in self._root_prims:
                raise KeyError(prim)

            prim = self._root_prims[prim]
        else:
            if prim._layer is not self:
                raise ValueError(f"{prim} is not a root of current layer")

        prim._set_layer(None)
        del self._root_prims[prim.name]
        self._touch()
        return prim

    def def_(self, prim_type:Type[PrimType], path:str)->PrimType:
        prim = prim_type(specifier = Specifier.Def)
        self[path] = prim
        return prim

    def class_(self, path:str)->PrimSpec:
        prim = PrimSpec(specifier = Specifier.Class)
        self[path] = prim
        return prim

    def over_(self, path:str)->PrimSpec:
        prim = PrimSpec(specifier = Specifier.Over)
        self[path] = prim
        return prim

    def root_prim(self, name:str)->PrimSpec:
        return self._root_prims[name]

    def __str__(self)->str:
        return f'Layer("{self.file_name}")'

    def save(self, file_name:str="")->None:
        LayerSerializer.save(self, file_name)
        self._impl._dirty = False
        self._impl._loaded = True

    def to_str(self)->str:
        return LayerSerializer.to_str(self)
