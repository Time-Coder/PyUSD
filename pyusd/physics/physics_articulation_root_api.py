from ..api_schema_base import APISchemaBase
from ..common import SchemaKind


class PhysicsArticulationRootAPI(APISchemaBase):
    """PhysicsArticulationRootAPI can be applied to a scene graph node, 
    and marks the subtree rooted here for inclusion in one or more reduced 
    coordinate articulations. For floating articulations, this should be on
    the root body. For fixed articulations (robotics jargon for e.g. a robot 
    arm for welding that is bolted to the floor), this API can be on a direct 
    or indirect parent of the root joint which is connected to the world, or 
    on the joint itself..
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "ArticulationRootAPI"
        }
    }
