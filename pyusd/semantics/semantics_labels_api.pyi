from typing import List

from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..dtypes import token

class SemanticsLabelsAPI(APISchemaBase):
    """Application of labels for a prim for a taxonomy specified by the
    schema's instance name.

    See `UsdSemanticsLabelsQuery` for more information about computations and
    inheritance of semantics.
    """

    @property
    def __INSTANCE_NAME__(self)->AttributeSpec[List[token]]:
        """Array of labels specified directly at this prim."""

    @__INSTANCE_NAME__.setter
    def __INSTANCE_NAME__(self, value:List[token])->None: ...
