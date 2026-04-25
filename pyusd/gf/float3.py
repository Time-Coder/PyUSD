from .genVec3 import genVec3

import ctypes


class float3(genVec3):
    
    @property
    def dtype(self)->type:
        return ctypes.c_float
    

class color3f(float3):
    pass

class point3f(float3):
    pass

class normal3f(float3):
    pass

class vector3f(float3):
    pass

class texCoord3f(float3):
    pass