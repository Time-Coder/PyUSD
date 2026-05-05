from ..api_schema_base import APISchemaBase
from ..dtypes import namespace, token
from .collection import Collection
from .inputs import Inputs
from .light import Light
from .light_filter import LightFilter
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

