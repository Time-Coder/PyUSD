from .genMat3 import genMat3

import ctypes


class matrix3d(genMat3):

    @property
    def dtype(self)->type:
        return ctypes.c_double
    