from .genMat2 import genMat2
from .float2 import float2

import ctypes


class matrix2f(genMat2, ctypes.c_float*4):

    @staticmethod
    def subvec_type()->type:
        return float2
    