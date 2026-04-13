import ctypes

from .genQuat import genQuat


class quatf(genQuat):

    @property
    def dtype(self)->type:
        return ctypes.c_float