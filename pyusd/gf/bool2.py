import ctypes

from .genVec2 import genVec2


class bool2(genVec2):

    _fields_ = [
        ('x', ctypes.c_bool),
        ('y', ctypes.c_bool)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_bool
