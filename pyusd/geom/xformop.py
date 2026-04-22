from ..attribute import Attribute
from ..dtypes import double, namespace
from ..gf import double3, matrix4d
from ..prim import Prim

from typing import Any
from typeguard import typechecked


class XformOp(Attribute):

    _transform_ops = {
        "translate",
        "rotateXYZ",
        "rotateX",
        "rotateY",
        "rotateZ",
        "scale",
        "transform"
    }

    @typechecked
    def __init__(self, parent_prim:Prim)->None:
        Attribute.__init__(self, parent_prim, None, namespace, "xformOp", False)
        self._children["translate"] = Attribute(parent_prim, self, double3, "xformOp:translate", is_leaf=True)
        self._children["rotateXYZ"] = Attribute(parent_prim, self, double3, "xformOp:rotateXYZ", is_leaf=True)
        self._children["rotateX"] = Attribute(parent_prim, self, double, "xformOp:rotateX", is_leaf=True)
        self._children["rotateY"] = Attribute(parent_prim, self, double, "xformOp:rotateY", is_leaf=True)
        self._children["rotateZ"] = Attribute(parent_prim, self, double, "xformOp:rotateZ", is_leaf=True)
        self._children["scale"] = Attribute(parent_prim, self, double3, "xformOp:scale", is_leaf=True)
        self._children["transform"] = Attribute(parent_prim, self, matrix4d, "xformOp:transform", is_leaf=True)

    def __setattr__(self, name: str, value: Any) -> None:
        Attribute.__setattr__(self, name, value)

        if name not in XformOp._transform_ops:
            return

        full_name = "xformOp:" + name

        if full_name not in self._parent_prim.xformOpOrder:
            self._parent_prim.xformOpOrder.value.append(full_name)
