from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import namespace
from ..gf import vector3f
from ..common import SchemaKind


class PhysicsScene(Typed):
    """General physics simulation properties, required for simulation."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Scene"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.gravityDirection = Attribute(vector3f,
        doc=
        """Gravity direction vector in simulation world space. Will be
        normalized before use. A zero vector is a request to use the negative 
        upAxis. Unitless.
        """,
        metadata={
            "customData": {
                "apiName": "gravityDirection"
            },
            "displayName": "Gravity Direction"
        }
    )
    physics.gravityMagnitude = Attribute(float,
        value=float('-inf'),
        doc=
        """Gravity acceleration magnitude in simulation world space. 
        A negative value is a request to use a value equivalent to earth 
        gravity regardless of the metersPerUnit scaling used by this scene. 
        Units: distance/second/second.
        """,
        metadata={
            "customData": {
                "apiName": "gravityMagnitude"
            },
            "displayName": "Gravity Magnitude"
        }
    )
