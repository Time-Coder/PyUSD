from .api_schema_base import APISchemaBase
from .common import Kind, SchemaKind
from .dtypes import asset
from enum import Enum
from typing import Optional, Union, List, Dict, Any
from typeguard import typechecked


class ModelAPI(APISchemaBase):
    """UsdModelAPI is an API schema that provides an interface to a prim's
    model qualities, if it does, in fact, represent the root prim of a model.
    
    The first and foremost model quality is its \\em kind, i.e. the metadata 
    that establishes it as a model (See KindRegistry).  UsdModelAPI provides
    various methods for setting and querying the prim's kind, as well as
    queries (also available on UsdPrim) for asking what category of model
    the prim is.  See \\ref Usd_ModelKind "Kind and Model-ness".
    
    UsdModelAPI also provides access to a prim's \\ref Usd_Model_AssetInfo "assetInfo"
    data.  While any prim \\em can host assetInfo, it is common that published
    (referenced) assets are packaged as models, therefore it is convenient
    to provide access to the one from the other.
    
    \\todo establish an _IsCompatible() override that returns IsModel()
    \\todo GetModelInstanceName()
    """

    schema_kind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "nonApplied"
        }
    }

    class KindValidation(Enum):
        KindValidationNone = 0
        KindValidationModelHierarchy = 1

    @property
    def kind(self)->Kind:
        return self.metadata.kind
    
    @kind.setter
    @typechecked
    def kind(self, kind:Kind):
        self.metadata.kind = kind

    @typechecked
    def is_kind(self, base_kind:Kind, validation:KindValidation=KindValidation.KindValidationModelHierarchy)->bool:
        """Return true if the prim's kind metadata is or inherits from
        \p baseKind as defined by the Kind Registry.
        
        If \p validation is KindValidationModelHierarchy (the default), then
        this also ensures that if baseKind is a model, the prim conforms to
        the rules of model hierarchy, as defined by IsModel. If set to
        KindValidationNone, no additional validation is done.
        
        IsModel and IsGroup are preferrable to IsKind("model") as they are
        optimized for fast traversal.
        
        \note If a prim's model hierarchy is not valid, it is possible that
        that prim.IsModel() and 
        prim.IsKind("model", Usd.ModelAPI.KindValidationNone) return different
        answers. (As a corallary, this is also true for for prim.IsGroup())"""
        raise NotImplementedError()

    @property
    def is_model(self)->bool:
        """Return true if this prim represents a model, based on its kind
        metadata."""
        return self.metadata.kind == Kind.Model

    @property
    def is_group(self)->bool:
        """Return true if this prim represents a model group, based on its kind
        metadata."""
        return self.metadata.kind == Kind.Group
    
    @property
    def asset_identifier(self)->Optional[asset]:
        """Returns the model's asset identifier as authored in the composed 
        assetInfo dictionary.
        
        The asset identifier can be used to resolve the model's root layer via 
        the asset resolver plugin."""

        return self.metadata.assetInfo.identifier
    
    @asset_identifier.setter
    @typechecked
    def asset_identifier(self, identifier:Union[asset, str])->None:
        """Sets the model's asset identifier to the given asset path, \p identifier.
        
        \sa GetAssetIdentifier()"""

        if not isinstance(identifier, asset):
            identifier = asset(identifier)

        self.metadata.assetInfo.identifier = identifier
    
    @property
    def asset_name(self)->Optional[str]:
        """Returns the model's asset name from the composed assetInfo dictionary.
        
        The asset name is the name of the asset, as would be used in a database 
        query."""
        return self.metadata.assetInfo.name
    
    @asset_name.setter
    @typechecked
    def asset_name(self, asset_name:str)->None:
        """Sets the model's asset name to \p assetName.
        
        \sa GetAssetName()"""

        self.metadata.assetInfo.name = asset_name
    
    @property
    def asset_version(self)->Optional[str]:
        """Returns the model's resolved asset version.  
        
        If you publish assets with an embedded version, then you may receive 
        that version string.  You may, however, cause your authoring tools to 
        record the resolved version <em>at the time at which a reference to the 
        asset was added to an aggregate</em>, at the referencing site.  In 
        such a pipeline, this API will always return that stronger opinion, 
        even if the asset is republished with a newer version, and even though 
        that newer version may be the one that is resolved when the UsdStage is 
        opened."""

        return self.metadata.assetInfo.version
    
    @asset_version.setter
    def asset_version(self, asset_version:str)->None:
        """Sets the model's asset version string. 
        
        \sa GetAssetVersion()"""

        self.metadata.assetInfo.version = asset_version
    
    @property
    def payload_asset_dependencies(self)->Optional[List[asset]]:
        """Returns the list of asset dependencies referenced inside the 
        payload of the model.
        
        This typically contains identifiers of external assets that are 
        referenced inside the model's payload. When the model is created, this 
        list is compiled and set at the root of the model. This enables 
        efficient dependency analysis without the need to include the model's 
        payload."""
        return self.metadata.assetInfo.payloadAssetDependencies
    
    @payload_asset_dependencies.setter
    def payload_asset_dependencies(self, asset_dependencies:List[asset])->None:
        """Sets the list of external asset dependencies referenced inside the 
        payload of a model.
        
        \sa GetPayloadAssetDependencies()"""

        self.metadata.assetInfo.payloadAssetDependencies = asset_dependencies
    
    @property
    def asset_info(self)->Dict[str, Any]:
        """Returns the model's composed assetInfo dictionary.
        
        The asset info dictionary is used to annotate models with various 
        data related to asset management. For example, asset name,
        identifier, version etc.
        
        The elements of this dictionary are composed element-wise, and are 
        nestable."""

        return self.metadata.assetInfo
    
    @asset_info.setter
    @typechecked
    def asset_info(self, info:Dict[str, Any])->None:
        """Sets the model's assetInfo dictionary to \p info in the current edit 
        target."""

        self.metadata.assetInfo = info