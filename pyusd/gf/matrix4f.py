from .genMat4 import genMat4

import ctypes


class matrix4f(genMat4):

    @property
    def dtype(self)->type:
        return ctypes.c_float
    