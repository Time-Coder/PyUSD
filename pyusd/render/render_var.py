from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import string, token
from ..common import SchemaKind


class RenderVar(Typed):
    """A UsdRenderVar describes a custom data variable for
    a render to produce.  The prim describes the source of the data, which
    can be a shader output or an LPE (Light Path Expression), and also
    allows encoding of (generally renderer-specific) parameters that
    configure the renderer for computing the variable.
    
    \\note The name of the RenderVar prim drives the name of the data 
    variable that the renderer will produce.
    
    \\note In the future, UsdRender may standardize RenderVar representation
    for well-known variables under the sourceType `intrinsic`,
    such as _r_, _g_, _b_, _a_, _z_, or _id_.
    
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "className": "Var"
        }
    }

    class SourceType(token):
        Raw = "raw"
        Primvar = "primvar"
        Lpe = "lpe"
        Intrinsic = "intrinsic"


    dataType = Attribute(token, uniform=True, doc="The type of this channel, as a USD attribute type.")

    sourceName = Attribute(string,
        uniform=True,
        doc="""The renderer should look for an output of this name
        as the computed value for the RenderVar.
        """
    )

    sourceType = Attribute(SourceType,
        uniform=True,
        doc="""
        Indicates the type of the source.

        - "raw": The name should be passed directly to the
          renderer.  This is the default behavior.
        - "primvar":  This source represents the name of a primvar.
          Some renderers may use this to ensure that the primvar
          is provided; other renderers may require that a suitable
          material network be provided, in which case this is simply
          an advisory setting.
        - "lpe":  Specifies a Light Path Expression in the
          [OSL Light Path Expressions language](https://github.com/imageworks/OpenShadingLanguage/wiki/OSL-Light-Path-Expressions) as the source for
          this RenderVar.  Some renderers may use extensions to
          that syntax, which will necessarily be non-portable.
        - "intrinsic":  This setting is currently unimplemented,
          but represents a future namespace for UsdRender to provide
          portable baseline RenderVars, such as camera depth, that
          may have varying implementations for each renderer.

        """
    )
