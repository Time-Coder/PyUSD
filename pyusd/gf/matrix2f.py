from .genMat2 import genMat2
from .float2 import float2

import ctypes


class matrix2f(genMat2):

    @property
    def dtype(self)->type:
        return ctypes.c_float

    @staticmethod
    def subvec_type()->type:
        return float2
    