from typing import Dict, List, Optional

from .common import Axis
from .metadata import Metadata

class LayerMetadata(Metadata):

    subLayers: List[str]
    relocates: Dict[str, str]
    defaultPrim: Optional[str]
    endTimeCode: Optional[float]
    metersPerUnit: Optional[float]
    startTimeCode: Optional[float]
    timeCodesPerSecond: Optional[float]
    upAxis: Axis
