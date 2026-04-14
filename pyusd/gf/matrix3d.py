from .genMat3 import genMat3
from .double3 import double3

import ctypes


class matrix3d(genMat3):

    @property
    def dtype(self)->type:
        return ctypes.c_double
    
    @staticmethod
    def subvec_type()->type:
        return double3