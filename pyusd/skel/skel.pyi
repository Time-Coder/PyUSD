from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from typing import List


class Skel(Attribute):

    @property
    def joints(self)->Attribute[List[token]]:
        """An (optional) array of tokens defining the list of
        joints to which jointIndices apply. If not defined, jointIndices applies
        to the ordered list of joints defined in the bound Skeleton's *joints*
        attribute. If undefined on a primitive, the primitive inherits the 
        value of the nearest ancestor prim, if any."""

    @joints.setter
    def joints(self, value:List[token])->None: ...

    @property
    def blendShapes(self)->Attribute[List[token]]:
        """An array of tokens defining the order onto which blend shape
        weights from an animation source map onto the *skel:blendShapeTargets*
        rel of a binding site. If authored, the number of elements must be equal
        to the number of targets in the _blendShapeTargets_ rel. This property
        is not inherited hierarchically, and is expected to be authored directly
        on the skinnable primitive to which the blend shapes apply."""

    @blendShapes.setter
    def blendShapes(self, value:List[token])->None: ...

    @property
    def animationSource(self)->Relationship:
        """Animation source to be bound to Skeleton primitives at or
        beneath the location at which this property is defined.
        """

    @animationSource.setter
    def animationSource(self, value:Relationship)->None: ...

    @property
    def skeleton(self)->Relationship:
        """Skeleton to be bound to this prim and its descendents that
        possess a mapping and weighting to the joints of the identified
        Skeleton."""

    @skeleton.setter
    def skeleton(self, value:Relationship)->None: ...

    @property
    def blendShapeTargets(self)->Relationship:
        """Ordered list of all target blend shapes. This property is not
        inherited hierarchically, and is expected to be authored directly on
        the skinnable primitive to which the the blend shapes apply."""

    @blendShapeTargets.setter
    def blendShapeTargets(self, value:Relationship)->None: ...
