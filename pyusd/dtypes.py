from typing import Any, Dict
from enum import ReprEnum


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

class token(str, ReprEnum):
    """
    Enum where members are also (and must be) strings
    """

    def __new__(cls, *values):
        "values must already be of type `str`"
        if len(values) > 3:
            raise TypeError('too many arguments for str(): %r' % (values, ))
        if len(values) == 1:
            # it must be a string
            if not isinstance(values[0], str):
                raise TypeError('%r is not a string' % (values[0], ))
        if len(values) >= 2:
            # check that encoding argument is a string
            if not isinstance(values[1], str):
                raise TypeError('encoding must be a string, not %r' % (values[1], ))
        if len(values) == 3:
            # check that errors argument is a string
            if not isinstance(values[2], str):
                raise TypeError('errors must be a string, not %r' % (values[2]))
        value = str(*values)
        member = str.__new__(cls, value)
        member._value_ = value
        return member

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """
        Return the lower-cased version of the member name.
        """
        return name.lower()

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

class opaque(object):
    pass

class group(opaque):
    pass

class namespace(opaque):
    pass

class dictionary(dict):
    
    def __getattr__(self, name:str)->Any:
        if name not in self:
            raise AttributeError(f"{name}")
        
        return self[name]
    
    def __setattr__(self, name:str, value:Any)->None:
        self[name] = value

    def update_one(self, key:str, value:Any)->None:
        list_op = ""
        if key.startswith("prepend "):
            list_op = "prepend"
        elif key.startswith("append "):
            list_op = "append"
        if list_op:
            key = key[len(list_op):].strip()
            if not isinstance(value, list):
                value = [value]

        if value is None and key in self and self[key] is not None:
            return

        if key in self and isinstance(self[key], dict) and isinstance(value, dict):
            dictionary.update(self[key], value)
        elif list_op == "prepend":
            self[key][:0] = value
        elif list_op == "append":
            self[key].extend(value)
        else:
            self[key] = value

    def update(self, kwargs:Dict[str, Any])->None:
        for key, value in kwargs.items():
            self.update_one(key, value)