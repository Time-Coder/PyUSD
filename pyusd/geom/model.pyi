from ..attribute_spec import AttributeSpec
from ..dtypes import asset, token
from ..gf import float3

class Model(AttributeSpec):

    class DrawMode(token):
        Origin = "origin"
        Bounds = "bounds"
        Cards = "cards"
        Default = "default"
        Inherited = "inherited"

    class CardGeometry(token):
        Cross = "cross"
        Box = "box"
        FromTexture = "fromTexture"


    @property
    def drawMode(self)->AttributeSpec[DrawMode]:
        """Alternate imaging mode; applied to this prim or child prims
                 where \\em model:applyDrawMode is true, or where the prim
                 has kind \\em component and \\em model:applyDrawMode is not
                 authored. See \\ref UsdGeomModelAPI_drawMode
                 for mode descriptions."""

    @drawMode.setter
    def drawMode(self, value:DrawMode)->None: ...

    @property
    def applyDrawMode(self)->AttributeSpec[bool]:
        """If true, and the resolved value of \\em model:drawMode is
                 non-default, apply an alternate imaging mode to this prim. See
                 \\ref UsdGeomModelAPI_drawMode."""

    @applyDrawMode.setter
    def applyDrawMode(self, value:bool)->None: ...

    @property
    def drawModeColor(self)->AttributeSpec[float3]:
        """The base color of imaging prims inserted for alternate
                 imaging modes. For \\em origin and \\em bounds modes, this
                 controls line color; for \\em cards mode, this controls the
                 fallback quad color."""

    @drawModeColor.setter
    def drawModeColor(self, value:float3)->None: ...

    @property
    def cardGeometry(self)->AttributeSpec[CardGeometry]:
        """The geometry to generate for imaging prims inserted for \\em
                 cards imaging mode. See \\ref UsdGeomModelAPI_cardGeometry for
                 geometry descriptions."""

    @cardGeometry.setter
    def cardGeometry(self, value:CardGeometry)->None: ...

    @property
    def cardTextureXPos(self)->AttributeSpec[asset]:
        """In \\em cards imaging mode, the texture applied to the X+ quad.
                 The texture axes (s,t) are mapped to model-space axes (-y, -z)."""

    @cardTextureXPos.setter
    def cardTextureXPos(self, value:asset)->None: ...

    @property
    def cardTextureYPos(self)->AttributeSpec[asset]:
        """In \\em cards imaging mode, the texture applied to the Y+ quad.
                 The texture axes (s,t) are mapped to model-space axes (x, -z)."""

    @cardTextureYPos.setter
    def cardTextureYPos(self, value:asset)->None: ...

    @property
    def cardTextureZPos(self)->AttributeSpec[asset]:
        """In \\em cards imaging mode, the texture applied to the Z+ quad.
                 The texture axes (s,t) are mapped to model-space axes (x, -y)."""

    @cardTextureZPos.setter
    def cardTextureZPos(self, value:asset)->None: ...

    @property
    def cardTextureXNeg(self)->AttributeSpec[asset]:
        """In \\em cards imaging mode, the texture applied to the X- quad.
                 The texture axes (s,t) are mapped to model-space axes (y, -z)."""

    @cardTextureXNeg.setter
    def cardTextureXNeg(self, value:asset)->None: ...

    @property
    def cardTextureYNeg(self)->AttributeSpec[asset]:
        """In \\em cards imaging mode, the texture applied to the Y- quad.
                 The texture axes (s,t) are mapped to model-space axes (-x, -z)."""

    @cardTextureYNeg.setter
    def cardTextureYNeg(self, value:asset)->None: ...

    @property
    def cardTextureZNeg(self)->AttributeSpec[asset]:
        """In \\em cards imaging mode, the texture applied to the Z- quad.
                 The texture axes (s,t) are mapped to model-space axes (-x, -y)."""

    @cardTextureZNeg.setter
    def cardTextureZNeg(self, value:asset)->None: ...
