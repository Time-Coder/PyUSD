from typing import Tuple, Union, TypeAlias
from .genMat import genMat
from .genVec3 import Vec3Type



class genMat3(genMat):

    @property
    def shape(self)->Tuple[int]:
        return (3, 3)
    
Mat3Type: TypeAlias = Union[genMat3, Tuple[Vec3Type, Vec3Type, Vec3Type]]
