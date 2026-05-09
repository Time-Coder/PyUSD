from .genVec3 import genVec3

import ctypes


class int3(genVec3):
    
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('z', ctypes.c_int)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_int