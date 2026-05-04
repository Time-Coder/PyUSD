from .render_settings_base import RenderSettingsBase
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..relationship import Relationship
from ..common import SchemaKind


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
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Product"
        }
    }

    class ProductType(token):
        Raster = "raster"
        DeepRaster = "deepRaster"


    productType: Attribute[ProductType] = Attribute(ProductType,
        uniform=True,
        value="raster",
        doc=
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
          per pixel at varying depths.
        """
    )

    productName: Attribute[token] = Attribute(token,
        value="",
        doc=
        """Specifies the name that the output/display driver
        should give the product.  This is provided as-authored to the
        driver, whose responsibility it is to situate the product on a
        filesystem or other storage, in the desired location.
        """
    )

    orderedVars: Relationship = Relationship(
        doc=
        """Specifies the RenderVars that should be consumed and
        combined into the final product.  If ordering is relevant to the
        output driver, then the ordering of targets in this relationship
        provides the order to use.
        """
    )
