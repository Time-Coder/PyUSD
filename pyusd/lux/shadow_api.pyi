from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..gf import color3f
from .inputs import Inputs


class ShadowAPI(APISchemaBase):
    """Controls to refine a light's shadow behavior.  These are
    non-physical controls that are valuable for visual lighting work.
    """

    @property
    def inputs(self) -> Inputs: ...

