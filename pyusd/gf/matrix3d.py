from .genMat3 import genMat3
from .double3 import double3

import ctypes


class matrix3d(genMat3, ctypes.c_double*9):
    
    @staticmethod
    def subvec_type()->type:
        return double3