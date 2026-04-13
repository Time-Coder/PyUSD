from .genMat2 import genMat2

import ctypes


class matrix2d(genMat2):

    @property
    def dtype(self)->type:
        return ctypes.c_double