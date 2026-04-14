from .genMat4 import genMat4
from .float4 import float4

import ctypes


class matrix4f(genMat4):

    @property
    def dtype(self)->type:
        return ctypes.c_float
    
    @staticmethod
    def subvec_type()->type:
        return float4