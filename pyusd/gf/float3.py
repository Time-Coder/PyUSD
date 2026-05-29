import ctypes

from .genVec3 import genVec3


class float3(genVec3):

    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_float
