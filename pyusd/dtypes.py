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
    """
    A USD token: an open-ended string, not a closed set of names.

    This was a ReprEnum, which made it unusable. An Enum's metaclass intercepts
    construction, so `token("default")` raised "has no members; specify
    `names=()`" and never reached the __new__ below -- which exists precisely to
    build one from a string. Nothing needed it to be an Enum either: it declares
    no members and nothing refers to one, so the base bought nothing and cost the
    ability to construct a value at all. That blocked every token-typed schema
    default from being emitted, since a default is written as a string literal.
    """

    def __new__(cls, *values):
        "values must already be of type `str`"
        if len(values) > 3:
            raise TypeError(f'too many arguments for str(): {values!r}')
        if len(values) == 1 and not isinstance(values[0], str):
            # it must be a string
            raise TypeError(f'{values[0]!r} is not a string')
        if len(values) >= 2 and not isinstance(values[1], str):
            # check that encoding argument is a string
            raise TypeError(f'encoding must be a string, not {values[1]!r}')
        if len(values) == 3 and not isinstance(values[2], str):
            # check that errors argument is a string
            raise TypeError(f'errors must be a string, not {values[2]!r}')
        value = str(*values)
        return str.__new__(cls, value)

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

class opaque:
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
            # Merge through the subclass, not the unbound method: the existing
            # value is often a plain dict (schema metadata arriving from a USDA
            # literal), and dictionary.update on it would look for update_one.
            # Converting first also keeps the invariant that anything stored here
            # supports attribute access.
            if not isinstance(self[key], dictionary):
                self[key] = dictionary(self[key])

            self[key].update(value)
        elif list_op == "prepend":
            self[key][:0] = value
        elif list_op == "append":
            self[key].extend(value)
        else:
            self[key] = value

    def update(self, *args: Any, **kwargs: Any)->None:
        # dict.update accepts several shapes. The single-mapping form is routed
        # through update_one so the "prepend "/"append " metadata keys work;
        # anything else keeps the plain dict behaviour.
        if len(args) == 1 and not kwargs and isinstance(args[0], dict):
            for key, value in args[0].items():
                self.update_one(key, value)

            return

        dict.update(self, *args, **kwargs)
