from ..api_schema_base import APISchemaBase
from ..dtypes import token


class SemanticsLabelsAPI(APISchemaBase):
    """Application of labels for a prim for a taxonomy specified by the
    schema's instance name.
    
    See `UsdSemanticsLabelsQuery` for more information about computations and
    inheritance of semantics.
    """

    @property
    def __INSTANCE_NAME__(self)->Attribute[List[token]]:
        """Array of labels specified directly at this prim."""

    @__INSTANCE_NAME__.setter
    def __INSTANCE_NAME__(self, value:List[token])->None: ...

