from __future__ import annotations
from typing import Dict, Union, Optional, TYPE_CHECKING
from typeguard import typechecked

if TYPE_CHECKING:
    from .Stage import Stage


class Prim:

    __name_indices:Dict[type, int] = {}
    
    def __init__(self, name:str="")->None:
        if name == "":
            name = self.__generate_name()

        self._stage:Stage = None
        self._name:str = name
        self._parent:Prim = None
        self._children:Dict[str, Prim] = {}

    def __getitem__(self, name:str)->Prim:
        if name not in self._children:
            self._children[name] = Prim(name)

        return self._children[name]
    
    @typechecked
    def __setitem__(self, name:str, prim:Prim)->None:
        self._children[name] = prim
        prim._parent = self
        prim._name = name

    @typechecked
    def __delitem__(self, name:str)->None:
        if name not in self._children:
            raise KeyError(name)
        
        prim:Prim = self._children[name]
        prim._parent = None
        prim.stage = None
        del self._children[name]

    @typechecked
    def add_child(self, prim:Prim)->None:
        if prim._parent is self:
            return
        
        if prim._parent is not None:
            prim.detach_from_parent()

        self._children[prim.name] = prim
        prim._parent = self
        prim.stage = self.stage

    @typechecked
    def remove_child(self, prim:Union[str, Prim])->Prim:
        if isinstance(prim, str):
            if prim not in self._children:
                raise KeyError(prim)
            
            prim = self._children[prim]
        else:
            if prim._parent != self:
                raise ValueError(f"{prim} is not a child of current prim")
            
        prim._parent = None
        prim.stage = None
        del self._children[prim.name]
        return prim

    def detach_from_parent(self)->None:
        if self._parent is None:
            return
        
        self._parent.remove_child(self)

    @property
    def name(self)->str:
        return self._name
    
    @name.setter
    @typechecked
    def name(self, name:str)->None:
        self._name = name

    @property
    def parent(self)->Prim:
        return self._parent
    
    @property
    def stage(self)->Stage:
        return self._stage
    
    @stage.setter
    def stage(self, stage:Optional[Stage])->None:
        self._stage = stage
        for child in self._children.values():
            child.stage = stage

    @property
    def path(self)->str:
        path:str = self._name
        prim:Prim = self
        while True:
            if prim._parent is not None:
                path = prim._parent.name + "/" + path
            else:
                path = "/" + path
                return path
    def __generate_name(self)->str:
        cls = self.__class__
        if cls not in Prim.__name_indices:
            Prim.__name_indices[cls] = 0

        index = Prim.__name_indices[cls]
        Prim.__name_indices[cls] += 1
        return cls.__name__ + str(index)
    
    def __repr__(self)->str:
        return self.__class__.__name__ + "(<" + self.path + ">)"