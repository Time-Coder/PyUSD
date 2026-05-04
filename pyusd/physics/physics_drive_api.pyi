from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace, token
from .physics import Physics

class PhysicsDriveAPI(APISchemaBase):
    """The PhysicsDriveAPI when applied to any joint primitive will drive
    the joint towards a given target. The PhysicsDriveAPI is a multipleApply 
    schema: drive can be set per axis "transX", "transY", "transZ", "rotX", 
    "rotY", "rotZ" or its "linear" for prismatic joint or "angular" for revolute 
    joints. Setting these as a multipleApply schema TfToken name will 
    define the degree of freedom the DriveAPI is applied to. Each drive is an 
    implicit force-limited damped spring: 
    Force or acceleration = stiffness * (targetPosition - position) 
    + damping * (targetVelocity - velocity)
    """


    class Type(token):
        Force = "force"
        Acceleration = "acceleration"

    @property
    def physics(self) -> Physics: ...

