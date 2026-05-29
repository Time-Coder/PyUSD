from typing import Any, Dict, List

from .metadata import Metadata
from .sdf import Specifier

class PrimMetadata(Metadata):

    specifier: Specifier
    typeName: str
    apiSchemas: List[str]
    assetInfo: Dict[str, Any]
    inherits: List[str]
    refrences: List[str]
    payloads: List[str]
    specializes: List[str]
    variantSets: List[str]
    variants: Dict[str, str]
