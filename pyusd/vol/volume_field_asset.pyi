from ..api_schema_base import APISchemaBase
from ..dtypes import asset, token
from .radiance import Radiance


class VolumeFieldAsset(APISchemaBase):
    "Base class for volume field primitives defined by an external file."


    class VectorDataRoleHint(token):
        None_ = "None"
        Point = "Point"
        Normal = "Normal"
        Vector = "Vector"
        Color = "Color"

    @property
    def filePath(self)->Attribute[asset]:
        """An asset path attribute that points to a file on disk.
                 For each supported file format, a separate FieldAsset
                 subclass is required. 
                  
                 This attribute's value can be animated over time, as most
                 volume asset formats represent just a single timeSample of
                 a volume.  However, it does not, at this time, support
                 any pattern substitutions like \"$F\". """

    @filePath.setter
    def filePath(self, value:asset)->None: ...

    @property
    def fieldName(self)->Attribute[token]:
        """Name of an individual field within the file specified by
                 the filePath attribute."""

    @fieldName.setter
    def fieldName(self, value:token)->None: ...

    @property
    def fieldIndex(self)->Attribute[int]:
        """A file can contain multiple fields with the same
                 name. This optional attribute is an index used to
                 disambiguate between these multiple fields with the same
                 name."""

    @fieldIndex.setter
    def fieldIndex(self, value:int)->None: ...

    @property
    def fieldDataType(self)->Attribute[token]:
        """Token which is used to indicate the data type of an
                 individual field. Authors use this to tell consumers more
                 about the field without opening the file on disk. The list of 
                 allowed tokens is specified with the specific asset type. 
                 A missing value is considered an error."""

    @fieldDataType.setter
    def fieldDataType(self, value:token)->None: ...

    @property
    def vectorDataRoleHint(self)->Attribute[VectorDataRoleHint]:
        """Optional token which is used to indicate the role of a vector
                 valued field. This can drive the data type in which fields
                 are made available in a renderer or whether the vector values 
                 are to be transformed."""

    @vectorDataRoleHint.setter
    def vectorDataRoleHint(self, value:VectorDataRoleHint)->None: ...

