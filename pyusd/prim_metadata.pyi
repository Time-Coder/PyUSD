from .metadata import Metadata
from .sdf import Specifier
from typing import List, Dict, Any


class PrimMetadata(Metadata):

    specifier: Specifier
    typeName: str
    apiSchemas: List[str]
    assetInfo: Dict[str, Any]
    inherits: str