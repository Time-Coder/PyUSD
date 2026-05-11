from .genMat4 import genMat4
from .double4 import double4

import ctypes


class matrix4d(genMat4, ctypes.c_double*16):
    
    @staticmethod
    def subvec_type()->type:
        return double4
    

class frame4d(matrix4d):
    pass