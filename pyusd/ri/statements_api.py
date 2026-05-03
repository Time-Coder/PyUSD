from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class StatementsAPI(APISchemaBase):
    """Container namespace schema for all renderman statements.

    \
ote The longer term goal is for clients to go directly to primvar
    or render-attribute API's, instead of using UsdRi StatementsAPI
    for inherited attributes.  Anticpating this, StatementsAPI
    can smooth the way via a few environment variables:

    * USDRI_STATEMENTS_READ_OLD_ENCODING: Causes StatementsAPI to read
      old-style attributes instead of primvars in the "ri:"
      namespace.
    """
    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "extraIncludes": """
                #include "pxr/usd/usdGeom/primvarsAPI.h"
                """
        }
    }
