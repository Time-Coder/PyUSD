from ..dtypes import token


class Specifier(token):
    Def = "def"
    Over = "over"
    Class = "class"


class Purpose(token):
    Default = "default"
    Public = "public"
    Private = "private"
    Hidden = "hidden"
    Internal = "internal"
