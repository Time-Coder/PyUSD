from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class SceneGraphPrimAPI(APISchemaBase):
    """
    Utility schema for display properties of a prim
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    ui: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    ui.displayName = Attribute(token,
        uniform=True,
        doc="""When publishing a nodegraph or a material, it can be useful to
        provide an optional display name, for readability.

        """,
        metadata={
            "customData": {
                "apiName": "displayName"
            }
        }
    )
    ui.displayGroup = Attribute(token,
        uniform=True,
        doc="""When publishing a nodegraph or a material, it can be useful to
        provide an optional display group, for organizational purposes and 
        readability. This is because often the usd shading hierarchy is rather
        flat while we want to display it in organized groups.

        """,
        metadata={
            "customData": {
                "apiName": "displayGroup"
            }
        }
    )
