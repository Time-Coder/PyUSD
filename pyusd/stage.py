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
    def __getitem__(self, name:str)->Prim:
        if name not in self._root_prims:
            prim = Prim(name)
            prim._set_stage(self)
            self._root_prims[name] = prim

        return self._root_prims[name]
    
    @typechecked
    def __setitem__(self, name:str, prim:Prim)->None:
        prim.detach_from_parent()
        prim.detach_from_stage()
        
        prim._name = name
        prim._set_stage(self)
        self._root_prims[name] = prim

    @typechecked
    def __delitem__(self, name:str)->None:
        if name not in self._root_prims:
            raise KeyError(name)
        
        prim:Prim = self._root_prims[name]
        prim._set_stage(None)
        del self._root_prims[name]

    @typechecked
    def add_prim(self, prim:Prim)->None:
        if prim._parent is None and prim._stage is self:
            return
        
        prim.detach_from_parent()
        prim.detach_from_stage()

        self._root_prims[prim.name] = prim
        prim._set_stage(self)

    @typechecked
    def remove_prim(self, prim:Union[str, Prim])->Prim:
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
    def def_(self, prim_type:type, name:str)->Prim:
        prim = prim_type(name)
        self.add_prim(prim)
        return prim
    
    def __repr__(self)->str:
        return f'Stage("{self.file_name}")'
    
    def to_str(self)->str:
        result = "#usda 1.0\n\n"
        for prim in self._root_prims.values():
            result += prim.to_str()

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