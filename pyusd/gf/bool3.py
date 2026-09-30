import ctypes

from .genVec3 import genVec3


class bool3(genVec3):

    _fields_ = [
        ('x', ctypes.c_bool),
        ('y', ctypes.c_bool),
        ('z', ctypes.c_bool)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_bool
