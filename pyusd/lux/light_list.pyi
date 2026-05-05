from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from typing import List


class LightList(Attribute):

    class CacheBehavior(token):
        ConsumeAndHalt = "consumeAndHalt"
        ConsumeAndContinue = "consumeAndContinue"
        Ignore = "ignore"


    @property
    def cacheBehavior(self)->Attribute[CacheBehavior]:
        """
        Controls how the lightList should be interpreted.
        Valid values are:
        - consumeAndHalt: The lightList should be consulted,
          and if it exists, treated as a final authoritative statement
          of any lights that exist at or below this prim, halting
          recursive discovery of lights.
        - consumeAndContinue: The lightList should be consulted,
          but recursive traversal over nameChildren should continue
          in case additional lights are added by descendants.
        - ignore: The lightList should be entirely ignored.  This
          provides a simple way to temporarily invalidate an existing
          cache.  This is the fallback behavior.
        """

    @cacheBehavior.setter
    def cacheBehavior(self, value:CacheBehavior)->None: ...
