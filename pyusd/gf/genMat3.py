from typing import Tuple
from .genMat import genMat


class genMat3(genMat):

    @property
    def shape(self)->Tuple[int]:
        return (3, 3)
    
genMat3 = genMat3