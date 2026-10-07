"""One composed variant set on a prim: the analogue of pxr's ``UsdVariantSet``.

Reads compose across the layer stack: the variant names are the union over the
contributing specs, strongest opinion first, and the selection is the strongest
authored one. Writing -- :meth:`select_variant`, :meth:`clear_selection`,
:meth:`block_selection` -- authors into the edit layer's spec, because variant
content has no stage path to hang a view on, and :meth:`__getitem__` is how that
content is shaped. The selection is a three-way opinion
rather than a name, which is what separates clearing it (drop this layer's
opinion, weaker layers compose through) from blocking it (author an empty
selection that stops them); pxr splits those the same way, and only the second one
is an authored value.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, List, Optional

from .variant_set_spec import VariantSetSpec

if TYPE_CHECKING:
    from .prim import Prim
    from .prim_spec import PrimSpec


class VariantSet:
    _prim: Prim
    _name: str

    def __init__(self, prim: Prim, name: str) -> None:
        self._prim = prim
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def _stored(self, spec: PrimSpec) -> Optional[VariantSetSpec]:
        """This layer's stored set, or None when it does not declare one.

        Membership rather than ``variant_set``, which raises: every walk here is
        over a stack of layers where a layer not declaring this set is the
        ordinary case, and ``__getitem__`` would declare it.
        """
        if self._name not in spec._variant_sets:
            return None

        return spec._variant_sets.variant_set(self._name)

    def variant_names(self) -> List[str]:
        names: List[str] = []
        seen: set[str] = set()
        for spec in self._specs():
            stored = self._stored(spec)
            if stored is None:
                continue

            for variant_name in stored:
                if variant_name not in seen:
                    seen.add(variant_name)
                    names.append(variant_name)

        return names

    def variant(self, name: str) -> PrimSpec:
        """The variant called ``name``, as the strongest contributing layer stores it.

        Raises ``KeyError`` when no contributing layer holds it. It is the read
        beside :meth:`__getitem__`, which declares the variant in the edit layer on
        a miss; use this when the variant should be read and nothing authored, and
        ``name in self`` to ask without raising either way.

        It walks the stack rather than asking one layer, which is what separates it
        from :meth:`~pyusd.variant_set_spec.VariantSetSpec.variant` -- that reads a
        single layer's copy, this one composes, the same direction the two classes
        differ in everywhere else.
        """
        for spec in self._specs():
            stored = self._stored(spec)
            if stored is None:
                continue

            if name in stored:
                return stored.variant(name)

        raise KeyError(name)

    def _specs(self) -> List[PrimSpec]:
        index = self._prim._stage._engine.prim_index(self._prim.path)
        return [source.prim for source in index.specs]

    @property
    def selection(self) -> Optional[str]:
        """The composed selection, strongest authored opinion first.

        ``None`` means no layer authors a selection at all, ``""`` is an authored
        empty selection (pxr's ``BlockVariantSelection``, which is what stops
        weaker layers), and anything else names the chosen variant.

        This walks the specs once. Asking through the handle instead --
        ``vs[name].selection`` -- costs two ``prim_index`` calls, because
        :meth:`~pyusd.variant_sets.VariantSets.__getitem__` checks presence before
        handing the handle back and each of those rebuilds the engine's cache key.
        """
        for spec in self._specs():
            stored = self._stored(spec)
            if stored is None:
                continue

            if stored.selection is not None:
                return stored.selection

        return None

    def select_variant(self, variant_name: str) -> None:
        """Author a selection in the edit layer, pxr's ``SetVariantSelection``.

        An empty name clears the edit layer's opinion instead of blocking the
        weaker ones, which is what pxr does; :meth:`block_selection` is the
        spelling for the other meaning.
        """
        variant_set = self._prim._edit_spec()._variant_sets[self._name]
        variant_set.select_variant(variant_name)
        self._prim._stage.invalidate()

    def clear_selection(self) -> None:
        """Drop the edit layer's selection, pxr's ``ClearVariantSelection``.

        The weaker layers' opinions compose through again, so the composed
        selection can become a variant this layer never mentioned.
        """
        self._prim._edit_spec()._variant_sets[self._name].clear_variant_selection()
        self._prim._stage.invalidate()

    def block_selection(self) -> None:
        """Author an empty selection in the edit layer, pxr's ``BlockVariantSelection``.

        This is an opinion rather than a removal: the composed selection becomes
        ``""`` and no layer's variant content is composed for this set.
        """
        self._prim._edit_spec()._variant_sets[self._name].block_variant_selection()
        self._prim._stage.invalidate()

    def __getitem__(self, name: str) -> PrimSpec:
        """The variant called ``name``, created in the edit layer if absent.

        The entry point to a variant's content, which is the one thing this class
        could not otherwise reach: a prim inside a variant has no absolute stage
        path, so there is no composed view to hand back and content has to be
        shaped as stored data. pxr gets there through ``GetVariantEditTarget``
        plus an ``UsdEditContext`` rather than through a subscript, and has
        ``AddVariant(name)`` for the creating half alone; pyusd has no edit
        targets, so this one call covers both -- declare it, then author into
        what comes back, exactly as the stored
        :class:`~pyusd.variant_set_spec.VariantSetSpec` does.

        Creating is the contract :meth:`~pyusd.variant_sets.VariantSets.__getitem__`
        already follows for a set that does not compose, so a miss here authors a
        variant rather than raising; :meth:`__contains__` is the side-effect-free
        way to ask.
        """
        variant = self._prim._edit_spec()._variant_sets[self._name][name]
        self._prim._stage.invalidate()
        # Remembered so the returned spec can act as an edit context: `with
        # vset["red"]:` needs the stage to push the target onto, and the spec
        # itself has no route back to one.
        variant._edit_stage = self._prim._stage
        variant._edit_root_path = self._prim.path
        return variant

    def __delitem__(self, name: str) -> None:
        """Drop the variant from the edit layer, leaving weaker opinions alone.

        The counterpart of :meth:`__getitem__` on the set that declared it, and
        pxr's ``RemoveVariant``. A variant declared only in a weak layer is not
        removable from here -- the edit layer does not hold it -- so this raises
        ``KeyError`` rather than reaching through the layer stack to edit
        someone else's opinion.
        """
        del self._prim._edit_spec()._variant_sets[self._name][name]
        self._prim._stage.invalidate()

    def __iter__(self) -> Iterator[str]:
        return iter(self.variant_names())

    def __len__(self) -> int:
        return len(self.variant_names())

    def __contains__(self, variant_name: str) -> bool:
        return variant_name in self.variant_names()
