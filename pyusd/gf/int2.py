from .genVec2 import genVec2

import ctypes


class int2(genVec2):
    
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_int