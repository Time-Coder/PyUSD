from .genMat4 import genMat4
from .double4 import double4

import ctypes


class matrix4d(genMat4):

    @property
    def dtype(self)->type:
        return ctypes.c_double
    
    @staticmethod
    def subvec_type()->type:
        return double4