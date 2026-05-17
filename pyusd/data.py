from typing import Any


class Data:

    def __init__(self, type:type, value:Any)->None:
        self.type = type
        self.value = value