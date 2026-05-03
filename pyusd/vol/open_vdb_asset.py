from .field_asset import FieldAsset
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..common import SchemaKind


class OpenVDBAsset(FieldAsset):
    """OpenVDB field primitive. The FieldAsset filePath attribute must
             specify a file in the OpenVDB format on disk."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    class Fielddatatype(token):
        Half = "half"
        Float = "float"
        Double = "double"
        Int = "int"
        Uint = "uint"
        Int64 = "int64"
        Half2 = "half2"
        Float2 = "float2"
        Double2 = "double2"
        Int2 = "int2"
        Half3 = "half3"
        Float3 = "float3"
        Double3 = "double3"
        Int3 = "int3"
        Matrix3d = "matrix3d"
        Matrix4d = "matrix4d"
        Quatd = "quatd"
        Bool = "bool"
        Mask = "mask"
        String = "string"

    class Fieldclass(token):
        Levelset = "levelSet"
        Fogvolume = "fogVolume"
        Staggered = "staggered"
        Unknown = "unknown"


    fieldDataType: Attribute[Fielddatatype] = Attribute(Fielddatatype,
        doc=
        """Token which is used to indicate the data type of an
                 individual field. Authors use this to tell consumers more
                 about the field without opening the file on disk. The list of 
                 allowed tokens reflects the available choices for OpenVDB 
                 volumes.
        """
    )

    fieldClass: Attribute[Fieldclass] = Attribute(Fieldclass,
        doc=
        """Optional token which can be used to indicate the class of
                 an individual grid. This is a mapping to openvdb::GridClass
                 where the values are GRID_LEVEL_SET, GRID_FOG_VOLUME, 
                 GRID_STAGGERED, and GRID_UNKNOWN.
        """
    )
