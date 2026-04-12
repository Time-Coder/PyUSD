from typing import Dict, Union
import os
from typeguard import typechecked

from .prim import Prim


class Stage:

    def __init__(self, file_name:str="")->None:
        self._file_name:str = file_name
        self._root_prims:Dict[str, Prim] = {}

    @property
    def file_name(self)->str:
        return self._file_name

    @typechecked
    def __getitem__(self, path:str)->Prim:
        if path.startswith("/"):
            path_items = path[1:].split("/")
        else:
            path_items = path.split("/")

        root_name = path_items[0]
        path_items = path_items[1:]
        root_prim = self._root_prims[root_name]
        return root_prim._getitem(path_items)
    
    @typechecked
    def __setitem__(self, path:str, prim:Prim)->None:
        if path.startswith("/"):
            path_items = path[1:].split("/")
        else:
            path_items = path.split("/")

        root_name = path_items[0]
        if len(path_items) == 1:
            prim.detach_from_parent()
            prim.detach_from_stage()
            
            prim._name = root_name
            prim._set_stage(self)
            self._root_prims[root_name] = prim
            return
        
        path_items = path_items[1:]
        if root_name not in self._root_prims:
            parent_prim = Prim(root_name)
            parent_prim._set_stage(self)
            self._root_prims[root_name] = parent_prim
        parent_prim = self._root_prims[root_name]
        parent_prim._setitem(path_items, prim)

    @typechecked
    def __delitem__(self, path:str)->None:
        if path.startswith("/"):
            path_items = path[1:].split("/")
        else:
            path_items = path.split("/")

        root_name = path_items[0]
        if len(path_items) == 1:
            if root_name not in self._root_prims:
                raise KeyError(root_name)
            
            prim:Prim = self._root_prims[root_name]
            prim._set_stage(None)
            del self._root_prims[root_name]
            return
        
        path_items = path_items[1:]
        parent_prim = self._root_prims[root_name]
        parent_prim._delitem(path_items)

    @typechecked
    def add_root_prim(self, prim:Prim)->None:
        if prim._parent is None and prim._stage is self:
            return
        
        prim.detach_from_parent()
        prim.detach_from_stage()

        self._root_prims[prim.name] = prim
        prim._set_stage(self)

    @typechecked
    def remove_root_prim(self, prim:Union[str, Prim])->Prim:
        if isinstance(prim, str):
            if prim not in self._root_prims:
                raise KeyError(prim)
            
            prim = self._root_prims[prim]
        else:
            if prim._stage is not self:
                raise ValueError(f"{prim} is not a root of current stage")
            
        prim._set_stage(None)
        del self._root_prims[prim.name]
        return prim
    
    @typechecked
    def def_(self, prim_type:type, path:str)->Prim:
        prim = prim_type()
        self[path] = prim
        return prim
    
    @typechecked
    def root_prim(self, name:str)->Prim:
        return self._root_prims[name]

    def __repr__(self)->str:
        return f'Stage("{self.file_name}")'
    
    def to_str(self)->str:
        result = "#usda 1.0\n\n"

        prims_str_list = []
        for prim in self._root_prims.values():
            prims_str_list.append(prim.to_str())

        result += "\n".join(prims_str_list)

        return result
    
    def save(self, file_name:str="")->None:
        if file_name == "":
            file_name = self._file_name

        abs_file_name = os.path.abspath(file_name)
        dir_name = os.path.dirname(abs_file_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(abs_file_name, "w") as f:
            f.write(self.to_str())