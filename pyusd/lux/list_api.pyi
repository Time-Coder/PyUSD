from ..api_schema_base import APISchemaBase
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
