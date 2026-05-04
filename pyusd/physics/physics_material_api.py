from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..common import SchemaKind


class PhysicsMaterialAPI(APISchemaBase):
    """ Adds simulation material properties to a Material. All collisions 
    that have a relationship to this material will have their collision response 
    defined through this material.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "className": "MaterialAPI"
        }
    }

    physics: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    physics.dynamicFriction = Attribute(float,
        doc="Dynamic friction coefficient. Unitless.",
        metadata={
            "customData": {
                "apiName": "dynamicFriction"
            },
            "displayName": "Dynamic Friction"
        }
    )
    physics.staticFriction = Attribute(float,
        doc="Static friction coefficient. Unitless.",
        metadata={
            "customData": {
                "apiName": "staticFriction"
            },
            "displayName": "Static Friction"
        }
    )
    physics.restitution = Attribute(float,
        doc="Restitution coefficient. Unitless.",
        metadata={
            "customData": {
                "apiName": "restitution"
            },
            "displayName": "Restitution"
        }
    )
    physics.density = Attribute(float,
        doc="""If non-zero, defines the density of the material. This can be
        used for body mass computation, see PhysicsMassAPI.
        Note that if the density is 0.0 it is ignored. 
        Units: mass/distance/distance/distance.
        """,
        metadata={
            "customData": {
                "apiName": "density"
            },
            "displayName": "Density"
        }
    )
