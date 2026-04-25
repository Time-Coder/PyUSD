from enum import Enum


class Specifier(Enum):
    Def = "def"
    Over = "over"
    Class = "class"

class Purpose(Enum):
    Default = "default"
    Public = "public"
    Private = "private"
    Hidden = "hidden"
    Internal = "internal"
