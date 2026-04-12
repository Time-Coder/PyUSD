from typing import List
from ..prim import Prim
from ..attribute import Attribute
from ..attribute_prefix import AttributePrefix


class XformOp(AttributePrefix):

    def __init__(self)->None:
        AttributePrefix.__init__(self, "xformOp")
        self._prop_names.extend(["translate", "rotateXYZ", "scale"])
        self._translate = Attribute("double3", "xformOp:translate")
        self._rotateXYZ = Attribute("double3", "xformOp:rotateXYZ")
        self._scale = Attribute("double3", "xformOp:scale")

    @property
    def translate(self)->Attribute:
        return self._translate
    
    @translate.setter
    def translate(self, value:List[float])->None:
        self._translate.value = value

    @property
    def rotateXYZ(self)->Attribute:
        return self._rotateXYZ
    
    @rotateXYZ.setter
    def rotateXYZ(self, value:List[float])->None:
        self._rotateXYZ.value = value

    @property
    def scale(self)->Attribute:
        return self._scale
    
    @scale.setter
    def scale(self, value:List[float])->None:
        self._scale.value = value


class Xform(Prim):

    def __init__(self, name:str="")->None:
        Prim.__init__(self, name)

        self._prop_names.append("xformOp")
        self._xformOp:XformOp = XformOp()

    @property
    def xformOp(self)->XformOp:
        return self._xformOp