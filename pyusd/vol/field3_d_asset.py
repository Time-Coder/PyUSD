from .field_asset import FieldAsset
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..common import SchemaKind


class Field3DAsset(FieldAsset):
    """Field3D field primitive. The FieldAsset filePath attribute must
             specify a file in the Field3D format on disk."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    class Fielddatatype(token):
        Half = "half"
        Float = "float"
        Double = "double"
        Half3 = "half3"
        Float3 = "float3"
        Double3 = "double3"


    fieldDataType: Attribute[Fielddatatype] = Attribute(Fielddatatype,
        doc=
        """Token which is used to indicate the data type of an
                 individual field. Authors use this to tell consumers more
                 about the field without opening the file on disk. The list of 
                 allowed tokens reflects the available choices for Field3d 
                 volumes.
        """
    )

    fieldPurpose: Attribute[token] = Attribute(token,
        doc=
        """Optional token which can be used to indicate the purpose or 
                 grouping of an individual field. Clients which consume Field3D 
                 files should treat this as the Field3D field \\em name.
        """
    )
