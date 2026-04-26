from typing import Any


class double(float):
    pass

class half(float):
    pass

class int64(int):
    pass

class asset(str):
    pass

class string(str):
    pass

class token(str):
    pass

class pathExpression(str):
    pass

class timecode(float):
    pass

class uchar(int):
    pass

class uint(int):
    pass

class uint64(int):
    pass

class namespace(object):
    pass

class opaque(object):
    pass

class group(opaque):
    pass

class dictionary(dict):
    
    def __getattr__(self, name:str)->Any:
        return self[name]
    
    def __setattr__(self, name:str, value:Any)->None:
        self[name] = value
