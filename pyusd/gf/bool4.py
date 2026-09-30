import ctypes

from .genVec4 import genVec4


class bool4(genVec4):

    _fields_ = [
        ('x', ctypes.c_bool),
        ('y', ctypes.c_bool),
        ('z', ctypes.c_bool),
        ('w', ctypes.c_bool)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_bool
