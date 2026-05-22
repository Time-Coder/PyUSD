from .genVec3 import genVec3

import ctypes


class double3(genVec3):
    
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_double
