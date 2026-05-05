from .render_settings_base import RenderSettingsBase
from ..dtypes import token
from .collection import Collection


class RenderProduct(RenderSettingsBase):
    """A UsdRenderProduct describes an image or other
    file-like artifact produced by a render. A RenderProduct
    combines one or more RenderVars into a file or interactive
    buffer.  It also provides all the controls established in
    UsdRenderSettingsBase as optional overrides to whatever the
    owning UsdRenderSettings prim dictates.
    
    Specific renderers may support additional settings, such
    as a way to configure compression settings, filetype metadata,
    and so forth.  Such settings can be encoded using
    renderer-specific API schemas applied to the product prim.
    
    """


    class ProductType(token):
        Raster = "raster"
        DeepRaster = "deepRaster"

    @property
    def productType(self)->Attribute[ProductType]:
        """
        The type of output to produce. Allowed values are ones most 
        renderers should be able to support.
        Renderers that support custom output types are encouraged to supply an 
        applied API schema that will add an `token myRenderContext:productType`
        attribute (e.g. `token ri:productType`), which will override this
        attribute's value for that renderer. 

        - "raster": This is the default type and indicates a 2D raster image of
          pixels.
        - "deepRaster": Indicates a deep image that contains multiple samples
          per pixel at varying depths."""

    @productType.setter
    def productType(self, value:ProductType)->None: ...

    @property
    def productName(self)->Attribute[token]:
        """Specifies the name that the output/display driver
        should give the product.  This is provided as-authored to the
        driver, whose responsibility it is to situate the product on a
        filesystem or other storage, in the desired location."""

    @productName.setter
    def productName(self, value:token)->None: ...

    @property
    def orderedVars(self)->Relationship:
        """Specifies the RenderVars that should be consumed and
        combined into the final product.  If ordering is relevant to the
        output driver, then the ordering of targets in this relationship
        provides the order to use."""

    @orderedVars.setter
    def orderedVars(self, value:Relationship)->None: ...

