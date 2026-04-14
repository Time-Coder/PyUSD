from ..attribute import Attribute


class XformOp(Attribute):

    def __init__(self)->None:
        Attribute.__init__(self, "namespace", "xformOp", False)
        self._children["translate"] = Attribute("double3", "xformOp:translate", True)
        self._children["rotateXYZ"] = Attribute("double3", "xformOp:rotateXYZ", True)
        self._children["rotateX"] = Attribute("double", "xformOp:rotateX", True)
        self._children["rotateY"] = Attribute("double", "xformOp:rotateY", True)
        self._children["rotateZ"] = Attribute("double", "xformOp:rotateZ", True)
        self._children["scale"] = Attribute("double3", "xformOp:scale", True)
        self._children["transform"] = Attribute("matrix4d", "xformOp:transform", True)
