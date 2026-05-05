from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import asset, token
from ..common import SchemaKind


class VolumeFieldAsset(APISchemaBase):
    "Base class for volume field primitives defined by an external file."

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    class VectorDataRoleHint(token):
        None_ = "None"
        Point = "Point"
        Normal = "Normal"
        Vector = "Vector"
        Color = "Color"


    filePath = Attribute(asset,
        doc="""An asset path attribute that points to a file on disk.
        For each supported file format, a separate FieldAsset
        subclass is required. 

        This attribute's value can be animated over time, as most
        volume asset formats represent just a single timeSample of
        a volume.  However, it does not, at this time, support
        any pattern substitutions like \"$F\". 
        """
    )

    fieldName = Attribute(token,
        doc="""Name of an individual field within the file specified by
        the filePath attribute.
        """
    )

    fieldIndex = Attribute(int,
        doc="""A file can contain multiple fields with the same
        name. This optional attribute is an index used to
        disambiguate between these multiple fields with the same
        name.
        """
    )

    fieldDataType = Attribute(token,
        doc="""Token which is used to indicate the data type of an
        individual field. Authors use this to tell consumers more
        about the field without opening the file on disk. The list of 
        allowed tokens is specified with the specific asset type. 
        A missing value is considered an error.
        """
    )

    vectorDataRoleHint = Attribute(VectorDataRoleHint,
        doc="""Optional token which is used to indicate the role of a vector
        valued field. This can drive the data type in which fields
        are made available in a renderer or whether the vector values 
        are to be transformed.
        """
    )
