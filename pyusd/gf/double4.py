import ctypes

from .genVec4 import genVec4


class double4(genVec4):

    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double),
        ('w', ctypes.c_double)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_double
