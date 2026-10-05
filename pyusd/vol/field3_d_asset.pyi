from enum import ReprEnum

from ..attribute_spec import AttributeSpec
from ..dtypes import token
from .field_asset import FieldAsset

class Field3DAsset(FieldAsset):
    """Field3D field primitive. The FieldAsset filePath attribute must
    specify a file in the Field3D format on disk.
    """


    class FieldDataType(token, ReprEnum):
        Half = "half"
        Float = "float"
        Double = "double"
        Half3 = "half3"
        Float3 = "float3"
        Double3 = "double3"

    @property
    def fieldDataType(self)->AttributeSpec[FieldDataType]:
        """Token which is used to indicate the data type of an
                 individual field. Authors use this to tell consumers more
                 about the field without opening the file on disk. The list of
                 allowed tokens reflects the available choices for Field3d
                 volumes."""

    @fieldDataType.setter
    def fieldDataType(self, value:FieldDataType)->None: ...

    @property
    def fieldPurpose(self)->AttributeSpec[token]:
        """Optional token which can be used to indicate the purpose or
                 grouping of an individual field. Clients which consume Field3D
                 files should treat this as the Field3D field \\em name."""

    @fieldPurpose.setter
    def fieldPurpose(self, value:token)->None: ...
