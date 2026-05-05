from ..api_schema_base import APISchemaBase
from ..gf import float2
from ..dtypes import asset, namespace, string, token
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

