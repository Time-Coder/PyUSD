from typing import Union, Tuple, TypeAlias
from .genVec import genVec
from .genType import Number


class genVec2(genVec):
    
    def __len__(self)->int:
        return 2

Vec2Type: TypeAlias = Union[genVec2, Tuple[Number, Number]]
