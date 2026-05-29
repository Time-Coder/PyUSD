import ctypes

from .genVec2 import genVec2


class double2(genVec2):

    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_double
