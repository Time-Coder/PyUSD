from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from typing import List


class Light(Attribute):

    class MaterialSyncMode(token):
        MaterialGlowTintsLight = "materialGlowTintsLight"
        Independent = "independent"
        NoMaterialResponse = "noMaterialResponse"


    @property
    def shaderId(self)->Attribute[token]:
        """Default ID for the light's shader. 
        This defines the shader ID for this light when a render context specific
        shader ID is not available. 

        The default shaderId for the intrinsic UsdLux lights (RectLight, 
        DistantLight, etc.) are set to default to the light's type name. For 
        each intrinsic UsdLux light, we will always register an SdrShaderNode in
        the SdrRegistry, with the identifier matching the type name and the 
        source type "USD", that corresponds to the light's inputs.
        \\see GetShaderId
        \\see GetShaderIdAttrForRenderContext
        \\see SdrRegistry::GetShaderNodeByIdentifier
        \\see SdrRegistry::GetShaderNodeByIdentifierAndType
        """

    @shaderId.setter
    def shaderId(self, value:token)->None: ...

    @property
    def materialSyncMode(self)->Attribute[MaterialSyncMode]:
        """
        For a LightAPI applied to geometry that has a bound Material, 
        which is entirely or partly emissive, this specifies the relationship 
        of the Material response to the lighting response.
        Valid values are:
        - materialGlowTintsLight: All primary and secondary rays see the 
          emissive/glow response as dictated by the bound Material while the 
          base color seen by light rays (which is then modulated by all of the 
          other LightAPI controls) is the multiplication of the color feeding 
          the emission/glow input of the Material (i.e. its surface or volume 
          shader) with the scalar or pattern input to *inputs:color*.
          This allows the light's color to tint the geometry's glow color while 
          preserving access to intensity and other light controls as ways to 
          further modulate the illumination.
        - independent: All primary and secondary rays see the emissive/glow 
          response as dictated by the bound Material, while the base color seen 
          by light rays is determined solely by *inputs:color*. Note that for 
          partially emissive geometry (in which some parts are reflective 
          rather than emissive), a suitable pattern must be connected to the 
          light's color input, or else the light will radiate uniformly from 
          the geometry.
        - noMaterialResponse: The geometry behaves as if there is no Material
          bound at all, i.e. there is no diffuse, specular, or transmissive 
          response. The base color of light rays is entirely controlled by the
          *inputs:color*. This is the standard mode for "canonical" lights in 
          UsdLux and indicates to renderers that a Material will either never 
          be bound or can always be ignored.
        """

    @materialSyncMode.setter
    def materialSyncMode(self, value:MaterialSyncMode)->None: ...

    @property
    def filters(self)->Relationship:
        """Relationship to the light filters that apply to this light."""

    @filters.setter
    def filters(self, value:Relationship)->None: ...
