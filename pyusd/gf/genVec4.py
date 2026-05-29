from typing import Tuple, TypeAlias, Union

from .genVec import Number, genVec


class genVec4(genVec):

    def __len__(self)->int:
        return 4

Vec4Type: TypeAlias = Union[genVec4, Tuple[Number, Number, Number, Number]]
