from typing import Any

from ..attribute_spec import AttributeSpec
from ..dtypes import double, namespace
from ..gf import double3, matrix4d, quatd
from ..property_spec import PropertySpec


class XformOp(AttributeSpec):

    translateX: AttributeSpec[double] = AttributeSpec(double, value=0.0, is_leaf=False)
    translateY: AttributeSpec[double] = AttributeSpec(double, value=0.0, is_leaf=False)
    translateZ: AttributeSpec[double] = AttributeSpec(double, value=0.0, is_leaf=False)
    translate: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    scale: AttributeSpec[double3] = AttributeSpec(double3, value=(1.0, 1.0, 1.0), is_leaf=False)
    scaleX: AttributeSpec[double] = AttributeSpec(double, value=1.0, is_leaf=False)
    scaleY: AttributeSpec[double] = AttributeSpec(double, value=1.0, is_leaf=False)
    scaleZ: AttributeSpec[double] = AttributeSpec(double, value=1.0, is_leaf=False)
    rotateX: AttributeSpec[double] = AttributeSpec(double, value=0.0, is_leaf=False)
    rotateY: AttributeSpec[double] = AttributeSpec(double, value=0.0, is_leaf=False)
    rotateZ: AttributeSpec[double] = AttributeSpec(double, value=0.0, is_leaf=False)
    rotateXYZ: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    rotateXZY: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    rotateYXZ: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    rotateYZX: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    rotateZXY: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    rotateZYX: AttributeSpec[double3] = AttributeSpec(double3, value=(0.0, 0.0, 0.0), is_leaf=False)
    orient: AttributeSpec[quatd] = AttributeSpec(quatd, value=(1.0, 0.0, 0.0, 0.0), is_leaf=False)
    transform: AttributeSpec[matrix4d] = AttributeSpec(matrix4d, value=matrix4d(), is_leaf=False)

    def __init__(self)->None:
        AttributeSpec.__init__(self, namespace, "xformOp", is_leaf=False)

    def _owner_prim(self):
        """The prim this op namespace is installed on, if any."""
        from ..prim_spec import PrimSpec

        owner = self
        while owner is not None:
            parent = owner._parent
            if parent is None:
                return None

            if isinstance(parent, PrimSpec):
                return parent

            owner = parent

        return None

    def __setattr__(self, name: str, value: Any) -> None:
        AttributeSpec.__setattr__(self, name, value)

        if "_props" not in self.__dict__ or name not in self._props:
            return

        parent_prim = self._owner_prim()
        if parent_prim is None:
            return

        full_name = self._name + ":" + name
        order = parent_prim.xformOpOrder
        current = order.get()
        if current is None:
            current = []
            order.value = current

        if full_name in current:
            return

        # xformOpOrder starts out as a schema fallback; authoring it is what makes
        # the op part of the transform stack, so the opinion has to be marked.
        current.append(full_name)
        order._value_state = PropertySpec.ValueState.Authored
