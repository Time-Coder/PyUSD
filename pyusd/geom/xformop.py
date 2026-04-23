from ..attribute import Attribute
from ..dtypes import double, namespace
from ..gf import double3, matrix4d

from typing import Any
from typeguard import typechecked


class XformOp(Attribute):

    @typechecked
    def __init__(self)->None:
        Attribute.__init__(self, namespace, "xformOp", is_leaf=False)
        self._add_prop(Attribute(double3, "translate", is_leaf=True))
        self._add_prop(Attribute(double3, "rotateXYZ", is_leaf=True))
        self._add_prop(Attribute(double, "rotateX", is_leaf=True))
        self._add_prop(Attribute(double, "rotateY", is_leaf=True))
        self._add_prop(Attribute(double, "rotateZ", is_leaf=True))
        self._add_prop(Attribute(double3, "scale", is_leaf=True))
        self._add_prop(Attribute(matrix4d, "transform", is_leaf=True))

    def __setattr__(self, name: str, value: Any) -> None:
        Attribute.__setattr__(self, name, value)

        if "_children" not in self.__dict__ or "_parent_prim" not in self.__dict__:
            return

        if name not in self._children:
            return

        full_name = self._name + ":" + name

        if full_name not in self._parent_prim.xformOpOrder:
            self._parent_prim.xformOpOrder.append(full_name)
