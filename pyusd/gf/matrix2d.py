from .genMat2 import genMat2
from .double2 import double2

import ctypes


class matrix2d(genMat2, ctypes.c_double*4):

    @staticmethod
    def subvec_type()->type:
        return double2