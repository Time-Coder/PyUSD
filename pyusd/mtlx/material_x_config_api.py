from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import string
from ..common import SchemaKind


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
            "apiSchemaCanOnlyApplyTo": None
        }
    }

    config: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    config.mtlx.version = Attribute(string,
        doc="""MaterialX library version that the data has been authored
        against. Defaults to 1.38 to allow correct verisoning of old files.
        """
    )
