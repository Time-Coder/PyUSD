from typing import Tuple, Dict, Any


class Metadata:

    def __init__(self, *args:Tuple[str], **kwargs:Dict[str, Any])->None: ...

    @property
    def customData(self)->Dict[str, Any]: ...

    def to_str(self, indents:int=0)->str: ...

    @property
    def doc(self)->str: ...

    @doc.setter
    def doc(self, doc:str)->None: ...