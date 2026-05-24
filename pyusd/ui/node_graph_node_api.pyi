from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..gf import color3f, float2
from ..dtypes import asset, string, token
from .ui import Ui


class NodeGraphNodeAPI(APISchemaBase):
    """
    This api helps storing information about nodes in node graphs.
    
    """


    class ExpansionState(token):
        Open = "open"
        Closed = "closed"
        Minimized = "minimized"

    @property
    def ui(self) -> Ui: ...

