from .genVec2 import genVec2

import ctypes


class float2(genVec2):

    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_float


class texCoord2f(float2):
    pass