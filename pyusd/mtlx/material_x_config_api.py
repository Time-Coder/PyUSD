from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, string


class MaterialXConfigAPI(APISchemaBase):
    """MaterialXConfigAPI is an API schema that provides an interface for
    storing information about the MaterialX environment.

    Initially, it only exposes an interface to record the MaterialX library
    version that data was authored against. The intention is to use this
    information to allow the MaterialX library to perform upgrades on data
    from prior MaterialX versions.

    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaCanOnlyApplyTo": ["Material"]
        }
    }

    config: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    config.mtlx.version = AttributeSpec(string,
        value="1.38",
        doc="""MaterialX library version that the data has been authored
        against. Defaults to 1.38 to allow correct verisoning of old files.
        """
    )
