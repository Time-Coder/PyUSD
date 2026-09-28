from typing import List, Optional, Dict

from .common import Axis
from .metadata import Metadata
from .prim import PrimSpec


class LayerMetadata(Metadata):

    subLayers: List[str]
    relocates: Dict[str, str]
    defaultPrim: Optional[PrimSpec]
    endTimeCode: Optional[float]
    metersPerUnit: Optional[float]
    startTimeCode: Optional[float]
    timeCodesPerSecond: Optional[float]
    upAxis: Axis
