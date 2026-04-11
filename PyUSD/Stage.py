from typing import Dict

from .Prim import Prim


class Stage:

    def __init__(self, file_name:str)->None:
        self.__file_name:str = file_name
        