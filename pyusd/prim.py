from __future__ import annotations
from typing import Dict, Union, Optional, TYPE_CHECKING
from typeguard import typechecked

if TYPE_CHECKING:
    from .stage import Stage


class Prim:

    __name_indices:Dict[type, int] = {}
    
    def __init__(self, name:str="")->None:
        if name == "":
            name = self.__generate_name()

        self._stage:Stage = None
        self._name:str = name
        self._parent:Prim = None
        self._children:Dict[str, Prim] = {}

    @typechecked
    def __getitem__(self, name:str)->Prim:
        if name not in self._children:
            prim = Prim(name)
            prim._set_stage(self._stage)
            prim._parent = self
            self._children[name] = prim

        return self._children[name]
    
    @typechecked
    def __setitem__(self, name:str, prim:Prim)->None:
        prim.detach_from_parent()
        prim.detach_from_stage()

        prim._parent = self
        prim._name = name
        prim._set_stage(self._stage)
        self._children[name] = prim

    @typechecked
    def __delitem__(self, name:str)->None:
        if name not in self._children:
            raise KeyError(name)
        
        prim:Prim = self._children[name]
        prim._parent = None
        prim._set_stage(None)
        del self._children[name]

    @typechecked
    def add_child(self, prim:Prim)->None:
        if prim._parent is self:
            return
        
        prim.detach_from_parent()
        prim.detach_from_stage()

        self._children[prim.name] = prim
        prim._parent = self
        prim._set_stage(self._stage)

    @typechecked
    def def_(self, prim_type:type, name:str)->Prim:
        prim = prim_type(name)
        self.add_child(prim)
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
        prim._set_stage(None)
        del self._children[prim.name]
        return prim

    def detach_from_parent(self)->None:
        if self._parent is None:
            return
        
        self._parent.remove_child(self)

    def detach_from_stage(self)->None:
        if self._stage is None or self._parent is not None:
            return
        
        self._stage.remove_prim(self)

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
    
    @typechecked
    def _set_stage(self, stage:Optional[Stage])->None:
        self._stage = stage
        for child in self._children.values():
            child._set_stage(stage)

    @property
    def path(self)->str:
        path:str = self._name
        prim:Prim = self
        while True:
            if prim._parent is not None:
                path = prim._parent.name + "/" + path
            else:
                if self.stage is not None:
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
    
    def __repr__(self)->str:
        return self.__class__.__name__ + "(<" + self.path + ">)"
    
    def to_str(self, indents:int=0)->str:
        tabs = "    " * indents
        result = f'{tabs}def {self.__class__.__name__} "{self.name}"\n'
        result += f'{tabs}{{\n'
        
        for child in self._children.values():
            result += child.to_str(indents + 1)

        result += f'{tabs}}}\n'
        return result
    