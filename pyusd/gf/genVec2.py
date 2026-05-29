from typing import Tuple, TypeAlias, Union

from .genType import Number
from .genVec import genVec


class genVec2(genVec):

    def __len__(self)->int:
        return 2

Vec2Type: TypeAlias = Union[genVec2, Tuple[Number, Number]]
