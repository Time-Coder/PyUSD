from .genVec3 import genVec3

import ctypes


class double3(genVec3):
    
    @property
    def dtype(self)->type:
        return ctypes.c_double
    

class color3d(double3):
    pass

class normal3d(double3):
    pass

class point3d(double3):
    pass

class vector3d(double3):
    pass

class texCoord3d(double3):
    pass