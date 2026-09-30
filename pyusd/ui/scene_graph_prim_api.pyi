from ..api_schema_base import APISchemaBase
from .ui import Ui

class SceneGraphPrimAPI(APISchemaBase):
    """
    Utility schema for display properties of a prim

    """

    @property
    def ui(self) -> Ui: ...
