from .genVec4 import genVec4

import ctypes


class float4(genVec4):
    
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
        ('w', ctypes.c_float)
    ]

    @property
    def dtype(self)->type:
        return ctypes.c_float
    
    
class color4f(float4):
    pass