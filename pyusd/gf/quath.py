import ctypes

from .genQuat import genQuat


class quath(genQuat):

    @property
    def dtype(self)->type:
        return ctypes.c_float
