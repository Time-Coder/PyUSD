from ..typed import Typed
from ..gf import vector3f
from .primvars import Primvars
from .skel import Skel


class BlendShape(Typed):
    """Describes a target blend shape, possibly containing inbetween
    shapes.
    
    See the extended \\ref UsdSkel_BlendShape "Blend Shape Schema
    documentation for information.
    
    """

    @property
    def offsets(self)->Attribute[List[vector3f]]:
        """**Required property**. Position offsets which, when added to the
        base pose, provides the target shape."""

    @offsets.setter
    def offsets(self, value:List[vector3f])->None: ...

    @property
    def normalOffsets(self)->Attribute[List[vector3f]]:
        """**Required property**. Normal offsets which, when added to the
        base pose, provides the normals of the target shape."""

    @normalOffsets.setter
    def normalOffsets(self, value:List[vector3f])->None: ...

    @property
    def pointIndices(self)->Attribute[List[int]]:
        """**Optional property**. Indices into the original mesh that
        correspond to the values in *offsets* and of any inbetween shapes. If
        authored, the number of elements must be equal to the number of elements
        in the *offsets* array."""

    @pointIndices.setter
    def pointIndices(self, value:List[int])->None: ...

