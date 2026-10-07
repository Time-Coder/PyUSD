from __future__ import annotations

from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
)

from .variant_set_serializer import VariantSetSerializer

if TYPE_CHECKING:
    from .prim_spec import PrimSpec


class VariantSetSpec:

    def __init__(self, name:str, parent_prim:PrimSpec)->None:
        self._name:str = name
        self._parent_prim:PrimSpec = parent_prim
        self._variants:Dict[str, PrimSpec] = {}
        # The selection is a tri-state, because pxr distinguishes three opinions
        # and they compose differently: None is no opinion from this layer, "" is
        # an authored empty selection (BlockVariantSelection) that stops weaker
        # layers, and anything else names the chosen variant. Clearing therefore
        # cannot be spelled as selecting "".
        self._selection:Optional[str] = None

    @property
    def name(self)->str:
        return self._name

    @property
    def selection(self)->Optional[str]:
        """This layer's own opinion: None, ``""`` when blocked, else a variant name."""
        return self._selection

    def select_variant(self, name:str)->Optional[PrimSpec]:
        """Author a selection in this layer, pxr's ``SetVariantSelection``.

        An empty name clears the opinion rather than blocking it, which is what
        pxr's ``SetVariantSelection("")`` means; ``block_variant_selection`` is the
        spelling that authors the empty selection.

        A selection is a field of its own and may name a variant this layer does
        not store -- pxr keeps the two apart, and authoring a variant here would
        invent content -- so the return is None in that case rather than an error.
        The selection is still recorded, which is what the returned None says.
        """
        if name == "":
            self.clear_variant_selection()
            return None

        self._selection = name
        self._parent_prim._touch()

        if name not in self._variants:
            return None

        return self._variants[name]

    def clear_variant_selection(self)->None:
        """Drop this layer's opinion, pxr's ``ClearVariantSelection``."""
        self._selection = None
        self._parent_prim._touch()

    def block_variant_selection(self)->None:
        """Author an empty selection, pxr's ``BlockVariantSelection``.

        ``""`` is a real opinion: composition stops there instead of falling
        through to a weaker layer's selection.
        """
        self._selection = ""
        self._parent_prim._touch()

    @property
    def selected_variant(self)->Optional[PrimSpec]:
        """The selected variant as this layer stores it, or None.

        None covers three cases -- no opinion, blocked, and a selection naming a
        variant this layer does not store -- and :attr:`selection` is what tells
        the first two apart from the third, since a selection and the content it
        names are separate fields. Membership rather than :meth:`variant` because
        every one of those three is an ordinary state of a layer, not a miss.
        """
        if not self._selection or self._selection not in self._variants:
            return None

        return self._variants[self._selection]

    def variant(self, name:str)->PrimSpec:
        """This layer's stored variant called ``name``.

        Raises ``KeyError`` when this layer does not store it. It is the read
        beside :meth:`__getitem__`, which creates a variant on a miss: use this
        when the answer is wanted and nothing should be authored.
        """
        return self._variants[name]

    def __getitem__(self, name:str)->PrimSpec:
        if not name:
            # PrimSpec.__init__ substitutes its own class name for an empty one, so
            # a nameless variant used to land in the layer as `variantSet { "PrimSpec" {} }`.
            raise ValueError("a variant needs a name")

        if name not in self._variants:
            from .prim_spec import PrimSpec

            variant = PrimSpec(name)
            variant._is_variant = True
            variant._parent = self._parent_prim
            self._variants[name] = variant
            self._parent_prim._touch()

        return self._variants[name]

    def __delitem__(self, name:str)->None:
        del self._variants[name]

    def keys(self)->KeysView[str]:
        return self._variants.keys()

    def values(self)->ValuesView[PrimSpec]:
        return self._variants.values()

    def items(self)->ItemsView[str, PrimSpec]:
        return self._variants.items()

    def __iter__(self)->Iterator[str]:
        return iter(self._variants)

    def __len__(self)->int:
        return len(self._variants)

    def __contains__(self, name:str)->bool:
        return name in self._variants

    def to_str(self, indents:int=0)->str:
        return VariantSetSerializer.to_str(self, indents)
