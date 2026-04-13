import ctypes

from .genQuat import genQuat


class quatd(genQuat):

    @property
    def dtype(self)->type:
        return ctypes.c_double