"""Composed variant sets on a prim: the analogue of pxr's ``UsdVariantSets``.

Reads compose across the layer stack -- a variant set declared only in a weak
layer is still a variant set of the prim -- while writes author into the edit
layer's spec, because variant content has no stage path to hang a view on.

Presence (``in``, ``len``, iteration) is a composed read. ``__getitem__`` is
both directions, keyed on composed presence: an existing set is a read and must
not create anything, a missing one is an authoring request and creates the set
in the edit layer -- the same lazy-creation contract as the stored
:class:`~pyusd.variant_sets_spec.VariantSetsSpec.__getitem__`, judged across
the layer stack. :meth:`get` is the non-creating lookup, so a question that must
not author anything asks it that way rather than reaching for the key.
Per-set operations live on :class:`VariantSet`.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Dict, List

from .variant_set import VariantSet

if TYPE_CHECKING:
    from .prim import Prim
    from .prim_spec import PrimSpec


class VariantSets:
    _prim: Prim

    def __init__(self, prim: Prim) -> None:
        self._prim = prim

    def _specs(self) -> List[PrimSpec]:
        """Contributing storage specs for the prim, strongest opinion first."""
        index = self._prim._stage._engine.prim_index(self._prim.path)
        return [source.prim for source in index.specs]

    def _declares(self, name: str) -> bool:
        """Whether any contributing layer holds this set, without creating one.

        Membership is the way to ask: ``__getitem__`` would declare the set in the
        edit layer, so reaching for the key to find out whether it exists would
        author the answer, and ``variant_set`` raises rather than answering, so it
        cannot be walked over a stack where a layer not declaring the set is the
        ordinary case.
        """
        return any(name in spec._variant_sets for spec in self._specs())

    def __getitem__(self, name: str) -> VariantSet:
        if not self._declares(name):
            # A key nothing composes is an authoring request, not a miss: the set
            # is created in the edit layer so the returned handle has something
            # to author into. A key some layer declares is a read and lands
            # here without creating anything.
            self._prim._edit_spec()._variant_sets[name]

        return VariantSet(self._prim, name)

    def get(self, name: str) -> VariantSet:
        """The composed set, pxr's own ``GetVariantSet``.

        Raises ``KeyError`` when no contributing layer declares it. It never
        creates, which is the whole point of it existing: a read through
        ``__getitem__`` authors a set into the edit layer, so reaching for the key
        would author the answer to "does this prim have that set". Membership
        answers that question without either behaviour -- ``__contains__`` never
        creates and never raises.
        """
        if not self._declares(name):
            raise KeyError(name)

        return VariantSet(self._prim, name)

    def variant_set(self, name: str) -> VariantSet:
        """Alias for :meth:`get`, matching the stored class's spelling."""
        return self.get(name)

    def __contains__(self, name: str) -> bool:
        return self._declares(name)

    def __iter__(self) -> Iterator[str]:
        names: List[str] = []
        seen: set[str] = set()
        for spec in self._specs():
            for set_name in spec._variant_sets:
                if set_name not in seen:
                    seen.add(set_name)
                    names.append(set_name)

        return iter(names)

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def all_variant_selections(self) -> Dict[str, str]:
        """Every selection authored on the prim, pxr's ``GetAllVariantSelections``.

        Only sets with an authored selection appear: a set that is merely declared
        has no opinion to report, and one whose selection was cleared drops out --
        which is what pxr's own dictionary does.

        This walks the specs itself rather than going through ``self[name]`` for
        each name. The subscript asks whether the set composes before handing back
        a handle, and that question costs a ``prim_index`` call of its own, so the
        subscript route rebuilt the engine's cache key -- a signature of the whole
        layer stack -- once per name on top of the walk below.

        ``_specs`` is strongest first, and the first opinion to name a set wins:
        a weaker layer selecting something else is exactly the case
        :meth:`~pyusd.variant_set.VariantSet.selection` resolves per set, so the
        two must agree. Every name reached here is one a spec declares, which is
        also what makes the presence check the subscript would have run already
        answered -- and keeps this read free of authoring.
        """
        selections: Dict[str, str] = {}
        for spec in self._specs():
            for name, variant_set in spec._variant_sets.items():
                if name in selections:
                    continue

                selection = variant_set.selection
                if selection is not None:
                    selections[name] = selection

        return selections
