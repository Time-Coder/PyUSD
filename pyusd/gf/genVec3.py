from typing import Union, Tuple, TypeAlias
from .genVec import genVec
from .genType import Number


class genVec3(genVec):
    
    def __len__(self)->int:
        return 3

Vec3Type: TypeAlias = Union[genVec3, Tuple[Number, Number, Number]]