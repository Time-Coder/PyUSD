from typing import Dict, List

from .dtypes import dictionary
from .metadata import Metadata
from .sdf import Specifier

class PrimMetadata(Metadata):

    specifier: Specifier
    typeName: str
    apiSchemas: List[str]
    assetInfo: dictionary
    inherits: List[str]
    refrences: List[str]
    payloads: List[str]
    specializes: List[str]
    variantSets: List[str]
    variants: Dict[str, str]
