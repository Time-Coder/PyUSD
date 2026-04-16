from ..attribute import Attribute
from ..dtypes import double, namespace
from ..gf import double3, matrix4d


class XformOp(Attribute):

    def __init__(self)->None:
        Attribute.__init__(self, namespace, "xformOp", False)
        self._children["translate"] = Attribute(double3, "xformOp:translate", is_leaf=True)
        self._children["rotateXYZ"] = Attribute(double3, "xformOp:rotateXYZ", is_leaf=True)
        self._children["rotateX"] = Attribute(double, "xformOp:rotateX", is_leaf=True)
        self._children["rotateY"] = Attribute(double, "xformOp:rotateY", is_leaf=True)
        self._children["rotateZ"] = Attribute(double, "xformOp:rotateZ", is_leaf=True)
        self._children["scale"] = Attribute(double3, "xformOp:scale", is_leaf=True)
        self._children["transform"] = Attribute(matrix4d, "xformOp:transform", is_leaf=True)
