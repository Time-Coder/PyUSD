from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token

class RenderProduct(Typed):

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

