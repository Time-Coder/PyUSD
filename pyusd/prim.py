from __future__ import annotations
from typing import Dict, Union, Optional, List, Any, TYPE_CHECKING
from typeguard import typechecked
import copy

from .property import Property
from .metadata import Metadata
from .utils import infer_type, in_annotations
from .sdf import Specifier
from .common import SchemaKind

if TYPE_CHECKING:
    from .layer import Layer


class Prim:

    __name_indices:Dict[type, int] = {}

    _name: str
    _layer: Optional[Layer]
    _metadata: Metadata
    _children: Dict[str, Prim]
    _parent: Optional[Prim]
    _props: Dict[str, Property]

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped
    meta: Dict[str, Any] = {}

    def __init__(self, name:str="")->None:
        if self.schema_kind in [SchemaKind.Invalid, SchemaKind.AbstractBase, SchemaKind.AbstractTyped]:
            raise TypeError(f"cannot instantiate abstract class {self.__class__.__name__}")

        if name == "":
            name = self.__generate_name()

        if not name.isidentifier():
            raise ValueError(f'"{name}" is not a valid name')
        
        self._layer:Optional[Layer] = None
        self._name:str = name
        self._parent:Optional[Prim] = None
        self._children:Dict[str, Prim] = {}
        self._props:Dict[str, Property] = {}
        self._metadata:Metadata = Metadata({
            "specifier": Specifier.Def,
            "typeName": self.__class__.__name__,
            "apiSchemas": [],
            "assetInfo": {
                "identifier": None,
                "name": None,
                "payloadAssetDependencies": None,
                "version": None
            }
        })

        if issubclass(self.__class__.__mro__[1], Prim) and self.__class__.__mro__[1] != Prim:
            self._metadata.update({"inherits": f"</{self.__class__.__mro__[1].__name__}>"})

        self._metadata.update({"doc": self.__class__.__doc__})

        for klass in self.__class__.__mro__:
            if klass is object:
                continue

            for name, value in klass.__dict__.items():
                if name not in self._props and isinstance(value, Property):
                    prop = value.clone()
                    prop._parent_prim = self
                    prop._name = name
                    self._props[name] = prop

        self._metadata.update(self.meta)
    
    def create_prop(self, prop:Property)->Property:
        self._props[prop.name] = prop
        prop._parent_prim = self
        prop._parent_prop = None
        return prop

    def _getitem(self, path_items:List[str])->Prim:
        prim = self
        for path_item in path_items:            
            prim = prim._children[path_item]

        return prim

    @typechecked
    def __getitem__(self, path:str)->Prim:
        if path.startswith("/"):
            raise ValueError("path must be relative")

        path_items = path.split("/")
        return self._getitem(path_items)
    
    def _setitem(self, path_items:List[str], prim:Prim)->None:
        name = path_items[-1]
        if not name.isidentifier():
            raise ValueError(f'"{name}" is not a valid name')
        
        path_items = path_items[:-1]
        parent_prim = self
        for path_item in path_items:
            if path_item not in parent_prim._children:
                new_prim = Prim(path_item)
                new_prim._set_layer(self._layer)
                new_prim._parent = parent_prim
                parent_prim._children[path_item] = new_prim
            parent_prim = parent_prim._children[path_item]

        prim.detach_from_parent()
        prim.detach_from_layer()

        prim._parent = parent_prim
        prim._name = name
        prim._set_layer(self._layer)
        parent_prim._children[name] = prim

    @typechecked
    def __setitem__(self, path:str, prim:Prim)->None:
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
        
        prim:Prim = parent_prim._children[name]
        prim._parent = None
        prim._set_layer(None)
        del parent_prim._children[name]

    @typechecked
    def __delitem__(self, path:str)->None:
        if path.startswith("/"):
            raise ValueError("path must be relative")
        
        path_items = path.split("/")
        self._delitem(path_items)

    @typechecked
    def prop(self, name:str)->Property:
        prop_names = name.split(":")
        prop_name = prop_names[0]
        if prop_name not in self._props:
            self.create_prop(Property(prop_name, custom=True, is_leaf=False))

        prop = self._props[prop_name]

        for prop_name in prop_names:
            if prop_name not in prop._children:
                prop.create_prop(Property(prop_name, custom=True, is_leaf=False))

            prop = prop._children[prop_name]

        return prop

    @typechecked
    def child(self, name:str)->Prim:
        return self._children[name]

    @typechecked
    def add_child(self, prim:Prim)->None:
        if prim._parent is self:
            return
        
        prim.detach_from_parent()
        prim.detach_from_layer()

        self._children[prim.name] = prim
        prim._parent = self
        prim._set_layer(self._layer)

    @typechecked
    def def_(self, prim_type:type, path:str)->Prim:
        prim = prim_type()
        self[path] = prim
        return prim

    @typechecked
    def remove_child(self, prim:Union[str, Prim])->Prim:
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
    def metadata(self)->Metadata:
        return self._metadata

    @property
    def name(self)->str:
        return self._name

    @name.setter
    @typechecked
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
        
        if old_parent is not None:
            if name in old_parent._children:
                raise ValueError(f'Prim with name "{name}" already exists in parent\'s children')
        elif old_layer is not None:
            if name in old_layer._root_prims:
                raise ValueError(f'Prim with name "{name}" already exists in layer\'s root prims')

        self.detach_from_parent()
        self.detach_from_layer()
        self._name = name

        if old_parent is not None:
            old_parent.add_child(self)
        elif old_layer is not None:
            old_layer.add_root_prim(self)

    @property
    def parent(self)->Prim:
        return self._parent
    
    @property
    def layer(self)->Layer:
        return self._layer
    
    @typechecked
    def _set_layer(self, layer:Optional[Layer])->None:
        self._layer = layer
        for child in self._children.values():
            child._set_layer(layer)

    @property
    def path(self)->str:
        path:str = self._name
        prim:Prim = self
        while True:
            if prim._parent is not None:
                path = prim._parent.name + "/" + path
                prim = prim._parent
            else:
                if self.layer is not None:
                    path = "/" + path
                    
                return path
            
    @property
    def depth(self)->int:
        depth:int = 0
        prim:Prim = self
        while True:
            if prim._parent is not None:
                depth += 1
                prim = prim._parent
            else:
                return depth
            
    def __generate_name(self)->str:
        cls = self.__class__
        if cls not in Prim.__name_indices:
            Prim.__name_indices[cls] = 0

        index = Prim.__name_indices[cls]
        Prim.__name_indices[cls] += 1
        return cls.__name__ + str(index)
    
    def __str__(self)->str:
        return self.__class__.__name__ + "(<" + self.path + ">)"
    
    def to_str(self, indents:int=0)->str:        
        tabs = "    " * indents
        prim_type_name = self.__class__.__name__
        if prim_type_name in ["Prim", "Typed"]:
            result = f'{tabs}def "{self.name}"'
        else:
            result = f'{tabs}def {prim_type_name} "{self.name}"'

        metadata_str = self._metadata.to_str(indents)
        if metadata_str:
            result += (" " + metadata_str)

        result += f'\n{tabs}{{\n'
        
        props_str_list = []
        for prop in self._props.values():
            prop_str = prop.to_str(indents+1)
            if prop_str:
                props_str_list.append(prop_str)

        if props_str_list:
            result += "\n".join(props_str_list) + "\n"

        children_str_list = []
        for child in self._children.values():
            children_str_list.append(child.to_str(indents + 1))

        if props_str_list and children_str_list:
            result += "\n"

        if children_str_list:
            result += "\n".join(children_str_list)

        result += f'{tabs}}}\n'
        return result
    
    @classmethod
    def cls_to_str(cls)->str:
        prim_type_name = cls.__name__
        if cls.schema_kind == SchemaKind.ConcreteTyped:
            result = f'class {prim_type_name} "{prim_type_name}"'
        else:
            result = f'class "{prim_type_name}"'

        if "meta" in cls.__dict__:
            metadata = Metadata(cls.meta)
        else:
            metadata = Metadata()

        update_metadata = {}

        if issubclass(cls.__mro__[1], Prim) and cls.__mro__[1] != Prim:
            update_metadata["inherits"] = f"</{cls.__mro__[1].__name__}>"

        if cls.__doc__:
            update_metadata["doc"] = cls.__doc__

        metadata.update(update_metadata)

        metadata_str = metadata.to_str(0, True)
        if metadata_str:
            result += (" " + metadata_str)

        result += f'\n{{\n'
        
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

        result += f'}}\n'
        return result

    def __getattr__(self, name:str)->Property:
        if name not in self._props:
            self.create_prop(Property(name, custom=True, is_leaf=False))

        return self._props[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return
        
        from .attribute import Attribute
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

        if name not in self._props and isinstance(value, Property):
            if value._parent_prim is None and value._parent_prop is None:
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

        self._props[name].set(value)
