from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import string, token

class RenderVar(Typed):

    class SourceType(token):
        Raw = "raw"
        Primvar = "primvar"
        Lpe = "lpe"
        Intrinsic = "intrinsic"

    @property
    def dataType(self)->Attribute[token]:
        """The type of this channel, as a USD attribute type."""

    @dataType.setter
    def dataType(self, value:token)->None: ...

    @property
    def sourceName(self)->Attribute[string]:
        """The renderer should look for an output of this name
        as the computed value for the RenderVar."""

    @sourceName.setter
    def sourceName(self, value:string)->None: ...

    @property
    def sourceType(self)->Attribute[SourceType]:
        """
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

    @sourceType.setter
    def sourceType(self, value:SourceType)->None: ...

