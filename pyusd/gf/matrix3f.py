from .genMat3 import genMat3

import ctypes


class matrix3f(genMat3):

    @property
    def dtype(self)->type:
        return ctypes.c_float
    