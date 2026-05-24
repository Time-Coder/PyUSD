from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from .light_list import LightList


class ListAPI(APISchemaBase):
    """
    \\deprecated
    Use LightListAPI instead
    
    """


    class CacheBehavior(token):
        ConsumeAndHalt = "consumeAndHalt"
        ConsumeAndContinue = "consumeAndContinue"
        Ignore = "ignore"

    @property
    def lightList(self) -> LightList: ...

    @property
    def lightList(self)->Relationship:
        """Relationship to lights in the scene."""

    @lightList.setter
    def lightList(self, value:Relationship)->None: ...

