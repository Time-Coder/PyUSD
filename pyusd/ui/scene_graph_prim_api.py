from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token


class SceneGraphPrimAPI(APISchemaBase):
    """
    Utility schema for display properties of a prim

    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    ui: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    ui.displayName = AttributeSpec(token,
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
    ui.displayGroup = AttributeSpec(token,
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
