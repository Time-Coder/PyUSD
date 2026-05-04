from ..api_schema_base import APISchemaBase
from ..dtypes import namespace
from .physics import Physics


class PhysicsLimitAPI(APISchemaBase):
    """The PhysicsLimitAPI can be applied to a PhysicsJoint and will
    restrict the movement along an axis. PhysicsLimitAPI is a multipleApply 
    schema: The PhysicsJoint can be restricted along "transX", "transY", 
    "transZ", "rotX", "rotY", "rotZ", "distance". Setting these as a 
    multipleApply schema TfToken name will define the degree of freedom the
    PhysicsLimitAPI is applied to. Note that if the low limit is higher than 
    the high limit, motion along this axis is considered locked.
    """

    @property
    def physics(self) -> Physics: ...

