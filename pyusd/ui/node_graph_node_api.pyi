from ..api_schema_base import APISchemaBase
from ..dtypes import token
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
