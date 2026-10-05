from enum import ReprEnum

from ..dtypes import token


class Specifier(token, ReprEnum):
    Def = "def"
    Over = "over"
    Class = "class"


class Purpose(token, ReprEnum):
    Default = "default"
    Public = "public"
    Private = "private"
    Hidden = "hidden"
    Internal = "internal"
