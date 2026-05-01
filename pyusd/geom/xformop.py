from ..attribute import Attribute
from ..dtypes import double, namespace
from ..gf import double3, matrix4d, quatd

from typing import Any
from typeguard import typechecked


class XformOp(Attribute):

    translateX: Attribute[double] = Attribute(double, value=0, is_leaf=False)
    translateY: Attribute[double] = Attribute(double, value=0, is_leaf=False)
    translateZ: Attribute[double] = Attribute(double, value=0, is_leaf=False)
    translate: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    scale: Attribute[double3] = Attribute(double3, value=(1, 1, 1), is_leaf=False)
    scaleX: Attribute[double] = Attribute(double, value=1, is_leaf=False)
    scaleY: Attribute[double] = Attribute(double, value=1, is_leaf=False)
    scaleZ: Attribute[double] = Attribute(double, value=1, is_leaf=False)
    rotateX: Attribute[double] = Attribute(double, value=0, is_leaf=False)
    rotateY: Attribute[double] = Attribute(double, value=0, is_leaf=False)
    rotateZ: Attribute[double] = Attribute(double, value=0, is_leaf=False)
    rotateXYZ: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    rotateXZY: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    rotateYXZ: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    rotateYZX: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    rotateZXY: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    rotateZYX: Attribute[double3] = Attribute(double3, value=(0, 0, 0), is_leaf=False)
    orient: Attribute[quatd] = Attribute(quatd, value=(1, 0, 0, 0), is_leaf=False)
    transform: Attribute[matrix4d] = Attribute(matrix4d, value=matrix4d(), is_leaf=False)

    @typechecked
    def __init__(self)->None:
        Attribute.__init__(self, namespace, "xformOp", is_leaf=False)

    def __setattr__(self, name: str, value: Any) -> None:
        Attribute.__setattr__(self, name, value)

        if "_children" not in self.__dict__ or "_parent_prim" not in self.__dict__:
            return

        if name not in self._children:
            return

        full_name = self._name + ":" + name

        if full_name not in self._parent_prim.xformOpOrder:
            self._parent_prim.xformOpOrder.append(full_name)
