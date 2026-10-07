from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, cast

from .dtypes import namespace, token
from .usda_serializer import UsdaSerializer
from .utils import (
    analyze_list_type,
    in_annotations,
    infer_type,
    nest_map,
    usd_matrix_types,
    usd_quat_types,
    usd_scalar_types,
    usd_vector_types,
)

T = TypeVar('T')


class _Arithmetic:
    """Element-wise operators over one value that can be read and written back.

    Two classes need these bodies and neither can inherit them from the other. Data
    owns a stored value; the composed Attribute in attribute.py reads its value out
    of composition and has to write into the edit layer instead. What the two
    genuinely share is the arithmetic, so that is what lives here, and the three
    methods a participant supplies are the whole contract:

      _read()          the value to compute on
      _write(value)    where an in-place result goes
      _other_value(x)  unwraps an operand that is itself one of these

    Nothing here says *where* the value lives, which is the only thing the two
    forms disagree about. An in-place operator ends in _write, so on a stored value
    it rewrites that object and on a composed handle it authors a new opinion --
    same body, one line of difference.

    Equality is deliberately absent: Data and Property each already define one and
    they agree, so moving it here would add a second definition without changing
    behaviour. __setitem__ is absent for the same reason it is not mirrored on the
    handle: it mutates the value it holds, which a value composed out of a layer
    stack cannot do.
    """

    def _read(self)->Any:
        raise NotImplementedError

    def _write(self, value:Any)->None:
        raise NotImplementedError

    @staticmethod
    def _other_value(other:Any)->Any:
        """Unwrap an operand that is itself one of these.

        Declared here because the bodies below call it, and left unimplemented on
        purpose: which of these an operand may be is one of the things the two forms
        disagree about, so each has to say which it accepts.
        """
        raise NotImplementedError

    def __add__(self, other:Any)->Any:
        return self._read() + self._other_value(other)

    def __radd__(self, other:Any)->Any:
        return self._other_value(other) + self._read()

    def __iadd__(self, other:Any)->Any:
        self._write(self._read() + self._other_value(other))
        return self

    def __sub__(self, other:Any)->Any:
        return self._read() - self._other_value(other)

    def __rsub__(self, other:Any)->Any:
        return self._other_value(other) - self._read()

    def __isub__(self, other:Any)->Any:
        self._write(self._read() - self._other_value(other))
        return self

    def __mul__(self, other:Any)->Any:
        return self._read() * self._other_value(other)

    def __rmul__(self, other:Any)->Any:
        return self._other_value(other) * self._read()

    def __imul__(self, other:Any)->Any:
        self._write(self._read() * self._other_value(other))
        return self

    def __truediv__(self, other:Any)->Any:
        return self._read() / self._other_value(other)

    def __rtruediv__(self, other:Any)->Any:
        return self._other_value(other) / self._read()

    def __itruediv__(self, other:Any)->Any:
        self._write(self._read() / self._other_value(other))
        return self

    def __floordiv__(self, other:Any)->Any:
        return self._read() // self._other_value(other)

    def __rfloordiv__(self, other:Any)->Any:
        return self._other_value(other) // self._read()

    def __ifloordiv__(self, other:Any)->Any:
        self._write(self._read() // self._other_value(other))
        return self

    def __mod__(self, other:Any)->Any:
        return self._read() % self._other_value(other)

    def __rmod__(self, other:Any)->Any:
        return self._other_value(other) % self._read()

    def __imod__(self, other:Any)->Any:
        self._write(self._read() % self._other_value(other))
        return self

    def __pow__(self, other:Any)->Any:
        return self._read() ** self._other_value(other)

    def __rpow__(self, other:Any)->Any:
        return self._other_value(other) ** self._read()

    def __ipow__(self, other:Any)->Any:
        self._write(self._read() ** self._other_value(other))
        return self

    def __gt__(self, other:Any)->bool:
        return self._read() > self._other_value(other)

    def __rgt__(self, other:Any)->bool:
        return self._other_value(other) > self._read()

    def __lt__(self, other:Any)->bool:
        return self._read() < self._other_value(other)

    def __rlt__(self, other:Any)->bool:
        return self._other_value(other) < self._read()

    def __ge__(self, other:Any)->bool:
        return self._read() >= self._other_value(other)

    def __rge__(self, other:Any)->bool:
        return self._other_value(other) >= self._read()

    def __le__(self, other:Any)->bool:
        return self._read() <= self._other_value(other)

    def __rle__(self, other:Any)->bool:
        return self._other_value(other) <= self._read()

    def __contains__(self, item:Any)->bool:
        return self._other_value(item) in self._read()


class Data(_Arithmetic, Generic[T]):

    _type: type
    _dtype: type
    _array_dim: int
    _value: Optional[T]

    def __init__(self, value_type: type, value: Optional[T])->None:
        dtype, array_dim = analyze_list_type(value_type)
        self._type:type = value_type
        self._dtype:type = dtype
        self._array_dim:int = array_dim
        self._value:Optional[T] = self._convert_from(value)

    @property
    def value(self)->Optional[T]:
        return self._value

    @value.setter
    def value(self, value:Optional[T])->None:
        self._value = value

    @property
    def type(self)->type:
        return self._type

    @property
    def type_name(self)->str:
        return UsdaSerializer.type_str(self._dtype, self._array_dim)

    @property
    def is_namespace(self)->bool:
        return (self._type == namespace)

    def value_str(self, indent:int=0)->str:
        return UsdaSerializer.value_str(self.value, indent)

    def get(self)->Optional[T]:
        return self.value

    def set(self, value:Optional[T])->None:
        self.value = value

    if not TYPE_CHECKING:
        def __getattr__(self, name:str)->Any:
            if hasattr(self._value, name):
                return getattr(self._value, name)

            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name:str, value:Any)->None:
        if hasattr(self.__class__, name) or in_annotations(name, self.__class__):
            super().__setattr__(name, value)
            return

        if hasattr(self._value, name):
            return setattr(self._value, name, value)
        else:
            return super().__setattr__(name, value)

    def _convert_from(self, value:Any)->Optional[T]:
        if value is None:
            return value

        current_type = infer_type(value)

        if isinstance(value, Data):
            value = value.value

        if value is None:
            return value

        if current_type is self._type or current_type is str and self._type is token:
            return value

        current_dtype, current_array_dim = analyze_list_type(current_type)
        if self._array_dim == current_array_dim and self._dtype is current_dtype:
            return value

        if self._array_dim != current_array_dim:
            raise TypeError(f"cannot convert {current_type} to {self._type}")

        if issubclass(self._dtype, usd_scalar_types):
            return nest_map(value, self._dtype)
        elif issubclass(self._dtype, usd_vector_types + usd_quat_types):
            if issubclass(current_dtype, Iterable):
                return nest_map(value, lambda x: self._dtype(*x))
            else:
                return nest_map(value, self._dtype)
        elif issubclass(self._dtype, usd_matrix_types):
            if issubclass(current_dtype, Iterable):

                def func(x):
                    args = []
                    subvec_type = cast(Any, self._dtype).subvec_type()
                    for sub_value in x:
                        if isinstance(sub_value, subvec_type):
                            args.append(sub_value)
                        elif isinstance(sub_value, Iterable):
                            args.append(subvec_type(*sub_value))
                        else:
                            args.append(subvec_type(sub_value))
                    return self._type(*args)

                return nest_map(value, func)
            else:
                return nest_map(value, self._dtype)
        else:
            raise TypeError(f"canot convert {current_type} to {self._type}")

    def _raw(self)->Any:
        """The stored value as-is.

        Operators below dispatch to whatever the dtype holds, and an unauthored
        value is None, so the operand is deliberately left untyped.
        """
        return self._value

    @staticmethod
    def _other_value(other:Any)->Any:
        if isinstance(other, Data):
            return other._raw()

        return other

    def _read(self)->Any:
        """What the shared arithmetic in _Arithmetic computes on."""
        return self._raw()

    def _write(self, value:Any)->None:
        """Where an in-place result lands. Here, on this stored object."""
        self.value = value

    def __str__(self)->str:
        return str(self.value)

    def __repr__(self)->str:
        return repr(self.value)

    def __eq__(self, other:Any)->bool:
        return (self._raw() == self._other_value(other))

    def __req__(self, other:Any)->bool:
        return (self._other_value(other) == self._raw())

    def __ne__(self, other:Any)->bool:
        return (self._raw() != self._other_value(other))

    def __rne__(self, other:Any)->bool:
        return (self._other_value(other) != self._raw())
    def __len__(self)->int:
        return len(self._raw())

    def __getitem__(self, name:Any)->Any:
        return self._raw()[self._other_value(name)]

    def __setitem__(self, name:Any, value:Any)->None:
        self._raw()[self._other_value(name)] = self._other_value(value)
