from typing import List, Optional

from .common import Axis
from .metadata import Metadata
from .prim import Prim

class LayerMetadata(Metadata):

    subLayers: List[str]
    defaultPrim: Optional[Prim]
    endTimeCode: Optional[float]
    metersPerUnit: Optional[float]
    startTimeCode: Optional[float]
    timeCodesPerSecond: Optional[float]
    upAxis: Axis
