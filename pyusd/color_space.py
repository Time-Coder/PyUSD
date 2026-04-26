from .attribute import Attribute
from .dtypes import namespace, token

from typeguard import typechecked


class ColorSpace(Attribute):

    @typechecked
    def __init__(self)->None:
        Attribute.__init__(self, namespace, "colorSpace", is_leaf=False)
        self.def_prop(Attribute(token, "name", uniform=True, is_leaf=True, metadata={
            "doc": """The color space that applies to attributes with
        unauthored color spaces on this prim and its descendents.
        """
        }))
