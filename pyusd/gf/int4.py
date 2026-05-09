from .genVec4 import genVec4

import ctypes


class int4(genVec4):

    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('z', ctypes.c_int),
        ('w', ctypes.c_int)
    ]
    
    @property
    def dtype(self)->type:
        return ctypes.c_int