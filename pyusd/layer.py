from __future__ import annotations

import os
import uuid
from collections.abc import Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)
from weakref import WeakValueDictionary

from beartype import beartype

from .common import Axis
from .layer_metadata import LayerMetadata
from .layer_parser import LayerParser
from .layer_serializer import LayerSerializer
from .prim_spec import PrimSpec
from .sdf import Specifier

if TYPE_CHECKING:
    from .prim import Prim, PrimType
    from .stage import Stage


class Layer:

    global_revision: ClassVar[int] = 0
    _registry: ClassVar[WeakValueDictionary[str, Layer]] = WeakValueDictionary()

    _file_name: str
    # Whether this layer was asked into existence rather than opened. It is the
    # single source of truth for "never read the file": Stage.__init__ consults it
    # when it would otherwise call Layer.load, and LayerCache.materialize consults
    # it when it would otherwise load lazily. One flag rather than two parameters
    # threading through both paths, because the lazy one is the one that surprises.
    _is_new: bool
    _identifier: str
    _root_prims: Dict[str, PrimSpec]
    _default_prim: Optional[PrimSpec]
    _sub_layers: List[Layer]
    _relocates: Dict[str, str]
    _metadata: LayerMetadata
    _revision: int
    _loaded: bool
    _dirty: bool
    _stage: Optional[Stage]
    # Relative asset paths authored through the API, mapped to the absolute file each
    # one was resolved to and the directory its stored spelling was made relative to.
    # A relative asset path is read relative to the layer holding it, so a path written
    # from elsewhere names one file when authored and another when read back. The
    # spelling in the layer is already correct for the directory it was authored
    # against; this remembers enough to re-express it if that directory ever changes,
    # which happens whenever an anonymous layer is first written somewhere or a named
    # one is saved under a different path.
    _cwd_relative_assets: Dict[str, Tuple[str, str]]
    _initialized: bool

    def __new__(cls, file_name: str = "", new: bool = False) -> Layer:
        # Interning by registry key is what makes `Layer(f) is Layer(f)` hold, and
        # with it the `is self` guards in add_root_prim / remove_root_prim: a spec
        # remembers the one layer object that owns it, so identity is the test.
        # `new=True` and anonymous layers take no part in this: a layer asked into
        # existence neither looks up nor registers, because an empty scratch layer
        # that merely carries a name is not that file's layer, so sharing or
        # clobbering one would be wrong in both directions. Two of those are
        # independent, in the same way two anonymous layers are.
        if new:
            return object.__new__(cls)

        key = cls._registry_key(str(file_name))
        if not key:
            return object.__new__(cls)

        existing = cls._registry.get(key)
        if existing is not None:
            return existing

        return object.__new__(cls)

    def __init__(self, file_name: str = "", new: bool = False) -> None:
        # __new__ may have handed back an interned instance, in which case Python
        # still calls __init__ with the new call's arguments. The state belongs to
        # the layer, not to this call, so a re-entry must not reset it.
        if getattr(self, "_initialized", False):
            return

        self._file_name: str = file_name
        self._is_new: bool = new
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
        self._stage = None
        self._cwd_relative_assets: Dict[str, Tuple[str, str]] = {}
        self._metadata._parent = self
        self._initialized = True

        if not new:
            key = self._registry_key(file_name)
            if key:
                Layer._registry[key] = self

    def touch(self) -> None:
        self._revision += 1
        self._dirty = True
        Layer.global_revision += 1

    @staticmethod
    def _root_name(path: str) -> str:
        return path.strip("/").split("/")[-1]

    @staticmethod
    def _relocate_key(prim: Union[PrimSpec, Any, str]) -> str:
        """Relocates are keyed by path so a view and its spec address the same entry."""
        if isinstance(prim, str):
            return prim

        path = getattr(prim, "path", None)
        if path is None:
            raise TypeError(f"cannot derive a relocates key from {prim!r}")

        return str(path)

    @property
    def stage(self) -> Stage:
        """A single-layer stage whose edit target is this layer.

        Created on first use so that layers only reached as composition inputs
        never pay for an engine they do not need. The stage is cached on the
        layer itself, and there is exactly one layer object per file name, so
        every access for one file sees the same one.
        """
        if self._stage is None:
            from .stage import Stage

            self._stage = Stage(self)

        return self._stage

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
    def _lookup(cls, file_name: str, anchor_file: str = "") -> Optional[Layer]:
        key = cls._registry_key(file_name, anchor_file)
        return cls._registry.get(key) if key else None

    @property
    def revision(self) -> int:
        return self._revision

    def _touch(self) -> None:
        self.touch()

    @staticmethod
    def load(file_name: str) -> Layer:
        return LayerParser.load(file_name)

    def relocate(self, prim: Union[PrimSpec, Any, str], new_path: str) -> None:
        self._relocates[self._relocate_key(prim)] = f"<{new_path}>"
        self._touch()

    def remove_relocate(self, prim: Union[PrimSpec, Any, str]) -> None:
        del self._relocates[self._relocate_key(prim)]
        self._touch()

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def metadata(self) -> LayerMetadata:
        return self._metadata

    @property
    def _default_prim_name(self) -> str:
        """Local default prim name, resolvable without building a stage view.

        Layer stack collection runs during composition, so anything it consults
        must not go through the stage: doing so re-enters the layer stack.
        """
        spec = self._default_prim
        if spec is not None:
            return spec.name

        value = self._metadata._builtin_data.get("defaultPrim")
        return str(value) if value else ""

    @property
    def default_prim(self) -> Optional[Prim]:
        from .prim import Prim as StagePrim

        name = self._default_prim_name
        if not name:
            return None

        return StagePrim(self.stage, "/" + name)

    @default_prim.setter
    def default_prim(self, prim: Union[PrimSpec, Any, str, None]) -> None:
        from .prim import Prim as StagePrim

        if prim is None:
            self._default_prim = None
            self.metadata.defaultPrim = None
            self._touch()
            return

        if isinstance(prim, StagePrim):
            prim_path = prim.path
        elif isinstance(prim, PrimSpec):
            if prim.layer is not self:
                raise ValueError("Prim is not in current layer")

            if prim.depth != 0:
                raise ValueError("Default prim must be a root prim")

            prim_path = prim.path
        else:
            prim_path = str(prim)
            if not prim_path.startswith("/"):
                prim_path = "/" + prim_path

        name = self._root_name(prim_path)
        spec = self._root_prims.get(name)
        if spec is None:
            raise ValueError(f"{prim_path} is not a root prim of this layer")

        self._default_prim = spec
        self.metadata.defaultPrim = name
        self._touch()

    def id(self, rel_layer: Optional[Union[str, Layer]] = None) -> str:
        if not self._file_name:
            return f"@{self._identifier}@"

        result: str = "@" + os.path.abspath(self._file_name).replace("\\", "/") + "@"
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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Layer):
            return (self.id() == other.id())
        elif isinstance(other, str):
            return (self.id().strip("@") == os.path.abspath(other.strip("@")).replace("\\", "/"))
        else:
            return False

    def __neq__(self, other: Any) -> bool:
        if isinstance(other, Layer):
            return (self.id() != other.id())
        elif isinstance(other, str):
            return (self.id().strip("@") != os.path.abspath(other.strip("@")).replace("\\", "/"))
        else:
            return True

    @beartype
    def include(self, layer: Layer, prepend: bool = True) -> None:
        if layer in self._sub_layers:
            return

        if prepend:
            self._sub_layers.insert(0, layer)
        else:
            self._sub_layers.append(layer)
        self._touch()

    @beartype
    def remove_include(self, layer: Layer) -> None:
        if layer not in self._sub_layers:
            return

        self._sub_layers.remove(layer)
        self._touch()

    def __getitem__(self, path: str) -> Prim:
        return self.stage[path]

    def __setitem__(self, path: str, prim: PrimSpec) -> None:
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

    def __delitem__(self, path: str) -> None:
        path_items = path[1:].split("/") if path.startswith("/") else path.split("/")

        root_name = path_items[0]
        if len(path_items) == 1:
            if root_name not in self._root_prims:
                raise KeyError(root_name)

            prim: PrimSpec = self._root_prims[root_name]
            prim._set_layer(None)
            del self._root_prims[root_name]
            self._touch()
            return

        path_items = path_items[1:]
        parent_prim = self._root_prims[root_name]
        parent_prim._delitem(path_items)
        self._touch()

    def add_root_prim(self, prim: PrimSpec) -> None:
        if prim._parent is None and prim._layer is self:
            return

        prim.detach_from_parent()
        prim.detach_from_layer()

        self._root_prims[prim.name] = prim
        prim._set_layer(self)
        self._touch()

    def remove_root_prim(self, prim: Union[str, PrimSpec]) -> PrimSpec:
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

    def def_(self, prim_type: Type[PrimType], path: str) -> PrimType:
        return self.stage.def_(prim_type, path)

    def class_(self, path: str) -> Prim:
        return self.stage.class_(path)

    def over_(self, path: str) -> Prim:
        return self.stage.over_(path)

    def root_prim(self, name: str) -> Prim:
        return self.stage["/" + name.lstrip("/")]

    def prim_at(self, path: str) -> Optional[Prim]:
        return self.stage.get_prim_at_path(path)

    def traverse(self, all: bool = False) -> Iterable[Prim]:
        """The composed prims of this layer's file, depth first.

        Goes through ``self.stage``, so the layer's own prims and its
        sub-layers' contributions both appear, in LIVRPS strength. The active
        rule is the stage's: an inactive prim and its subtree are skipped unless
        ``all`` is set (pxr's ``Traverse`` versus ``TraverseAll``).
        """
        return self.stage.traverse("/", all)

    def prim_spec_at(self, path: str) -> Optional[PrimSpec]:
        """The authored storage node at ``path``, if this layer defines one.

        The low-level escape hatch: views are the normal way to read and write,
        but operations that shape the stored data itself (create_attr, relocates,
        variant contents) still operate on the spec.
        """
        path = str(path)
        if not path.startswith("/"):
            path = "/" + path

        parts = [part for part in path.split("/") if part]
        if not parts:
            return None

        spec = self._root_prims.get(parts[0])
        for part in parts[1:]:
            if spec is None:
                return None

            spec = spec._children.get(part)

        return spec

    def __str__(self) -> str:
        return f'Layer("{self.file_name}")'

    def save(self, file_name: str = "") -> None:
        if file_name and file_name != self._file_name:
            # Saving elsewhere makes that the layer's address. Leaving the old name in
            # place is not merely cosmetic: a relative asset path is read relative to
            # the layer that holds it, so the layer would keep resolving against a
            # directory it no longer lives in. The registry is keyed on construction
            # and is not re-keyed here.
            self._file_name = file_name

        LayerSerializer.save(self, file_name)
        self._dirty = False
        self._loaded = True

    def to_str(self) -> str:
        return LayerSerializer.to_str(self)
