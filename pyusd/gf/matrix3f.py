from .genMat3 import genMat3
from .float3 import float3

import ctypes


class matrix3f(genMat3):

    @property
    def dtype(self)->type:
        return ctypes.c_float
    
    @staticmethod
    def subvec_type()->type:
        return float3