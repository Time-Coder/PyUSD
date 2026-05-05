from .nonboundable_light_base import NonboundableLightBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace
from ..dtypes import asset, token
from ..common import SchemaKind


class DomeLight(NonboundableLightBase):
    """Light emitted inward from a distant external environment,
    such as a sky or IBL light probe.
    
    In this version of the dome light, the dome's default orientation is such
    that its top pole is aligned with the world's +Y axis. This adheres to the
    OpenEXR specification for latlong environment maps.  From the OpenEXR
    documentation:
    
    -------------------------------------------------------------------------
    Latitude-Longitude Map:
    
    The environment is projected onto the image using polar coordinates
    (latitude and longitude).  A pixel's x coordinate corresponds to
    its longitude, and the y coordinate corresponds to its latitude.
    Pixel (dataWindow.min.x, dataWindow.min.y) has latitude +pi/2 and
    longitude +pi; pixel (dataWindow.max.x, dataWindow.max.y) has
    latitude -pi/2 and longitude -pi.
    
    In 3D space, latitudes -pi/2 and +pi/2 correspond to the negative and
    positive y direction.  Latitude 0, longitude 0 points into positive
    z direction; and latitude 0, longitude pi/2 points into positive x
    direction.
    
    The size of the data window should be 2*N by N pixels (width by height),
    where N can be any integer greater than 0.
    -------------------------------------------------------------------------
    
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    class Format(token):
        Automatic = "automatic"
        Latlong = "latlong"
        MirroredBall = "mirroredBall"
        Angular = "angular"
        CubeMapVerticalCross = "cubeMapVerticalCross"


    light: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    light.shaderId = Attribute(token,
        uniform=True,
        metadata={
            "customData": {
                "apiSchemaOverride": True
            }
        }
    )

    inputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    inputs.texture.file = Attribute(asset,
        doc="""A color texture to use on the dome, such as an HDR (high
        dynamic range) texture intended for IBL (image based lighting).
        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Color Map",
            "customData": {
                "apiName": "textureFile"
            }
        }
    )
    inputs.texture.format = Attribute(Format,
        doc="""
        Specifies the parameterization of the color map file.
        Valid values are:
        - automatic: Tries to determine the layout from the file itself.
          For example, Renderman texture files embed an explicit
          parameterization.
        - latlong: Latitude as X, longitude as Y.
        - mirroredBall: An image of the environment reflected in a
          sphere, using an implicitly orthogonal projection.
        - angular: Similar to mirroredBall but the radial dimension
          is mapped linearly to the angle, providing better sampling
          at the edges.
        - cubeMapVerticalCross: A cube map with faces laid out as a
          vertical cross.

        """,
        metadata={
            "displayGroup": "Basic",
            "displayName": "Color Map Format",
            "customData": {
                "apiName": "textureFormat"
            }
        }
    )

    guideRadius = Attribute(float,
        doc="The radius of guide geometry to use to visualize the dome light.  The default is 1 km for scenes whose metersPerUnit is the USD default of 0.01 (i.e., 1 world unit is 1 cm).",
        metadata={
            "displayGroup": "Guides",
            "displayName": "Radius"
        }
    )

    portals = Relationship(doc="Optional portals to guide light sampling.")
