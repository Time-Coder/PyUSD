from typing import Tuple
from .genMat import genMat


class genMat2(genMat):

    @property
    def shape(self)->Tuple[int]:
        return (2, 2)
    
genMat2 = genMat2