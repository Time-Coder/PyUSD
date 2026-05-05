from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import token
from typing import List


class Info(Attribute):

    class ImplementationSource(token):
        Id = "id"
        SourceAsset = "sourceAsset"
        SourceCode = "sourceCode"


    @property
    def implementationSource(self)->Attribute[ImplementationSource]:
        """Specifies the attribute that should be consulted to get the 
        shader's implementation or its source code.

        * If set to "id", the "info:id" attribute's value is used to 
        determine the shader source from the shader registry.
        * If set to "sourceAsset", the resolved value of the "info:sourceAsset" 
        attribute corresponding to the desired implementation (or source-type)
        is used to locate the shader source.  A source asset file may also
        specify multiple shader definitions, so there is an optional attribute
        "info:sourceAsset:subIdentifier" whose value should be used to indicate
        a particular shader definition from a source asset file.
        * If set to "sourceCode", the value of "info:sourceCode" attribute 
        corresponding to the desired implementation (or source type) is used as 
        the shader source.
        """

    @implementationSource.setter
    def implementationSource(self, value:ImplementationSource)->None: ...

    @property
    def id(self)->Attribute[token]:
        """The id is an identifier for the type or purpose of the 
        shader. E.g.: Texture or FractalFloat.
        The use of this id will depend on the render context: some will turn it
        into an actual shader path, some will use it to generate shader source 
        code dynamically.
        
        \\sa SetShaderId()
        """

    @id.setter
    def id(self, value:token)->None: ...
