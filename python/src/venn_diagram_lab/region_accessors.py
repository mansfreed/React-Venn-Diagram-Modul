"""Region accessor sugar.

Three exported helpers over :class:`RegionResult` for the most common
questions:

* ``intersection_items``: which items appear in every set in this group,
  regardless of other memberships?
* ``exclusive_items``: which items appear ONLY in this exact combination?
* ``union_items``: which items appear in any of these sets?

All three accept either set letters (``"A"``, ``"B"``, ...) or display
names (the values of ``result.dataset.set_names``). Inputs may mix both.
Sets argument is required and must be non-empty. Output ordering follows
``dataset.item_order`` for deterministic byte-equivalent results across
runs and across language implementations.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from venn_diagram_lab.analysis import RegionResult

__all__ = ["exclusive_items", "intersection_items", "union_items"]

_LETTERS = "ABCDEFGHI"


def _resolve_set_indices(result: RegionResult, sets: Sequence[str]) -> list[int]:
    """Resolve a sets-vector (mix of letters and display names) into 0-based indices."""
    if len(sets) == 0:
        raise ValueError("`sets` must contain at least one set identifier.")
    set_names = list(result.dataset.set_names)
    n = len(set_names)
    name_to_index = {name: i for i, name in enumerate(set_names)}
    letter_to_index = {_LETTERS[i]: i for i in range(n)}
    indices: list[int] = []
    for s in sets:
        if s in letter_to_index:
            indices.append(letter_to_index[s])
        elif s in name_to_index:
            indices.append(name_to_index[s])
        else:
            raise ValueError(f"Unknown set identifier: {s!r}")
    return indices


def _indices_to_mask(indices: Sequence[int]) -> int:
    """Convert a 0-based-index vector into the canonical bitmask."""
    mask = 0
    for i in indices:
        mask |= 1 << i
    return mask


def _ordered_items(
    result: RegionResult, item_filter: set[str]
) -> list[str]:
    """Return items in ``item_filter``, in dataset.item_order order."""
    item_order = result.dataset.item_order
    if item_order:
        return [it for it in item_order if it in item_filter]
    return sorted(item_filter)


def intersection_items(result: RegionResult, sets: Sequence[str]) -> list[str]:
    """Items appearing in every set in ``sets``, regardless of other memberships.

    Parameters
    ----------
    result : RegionResult
        Output of :func:`venn_diagram_lab.analyze`.
    sets : sequence of str
        Set letters (``"A"``, ``"B"``, ...) or display names from
        ``result.dataset.set_names``. May mix both forms.

    Returns
    -------
    list[str]
        Item identifiers shared by every named set, ordered by
        ``dataset.item_order``. Empty list if no item qualifies.
    """
    indices = _resolve_set_indices(result, sets)
    set_names = list(result.dataset.set_names)
    chosen_names = [set_names[i] for i in indices]
    if len(chosen_names) == 1:
        # Single set: all its members qualify.
        return _ordered_items(result, set(result.dataset.items[chosen_names[0]]))
    # Intersect membership sets.
    item_filter = set(result.dataset.items[chosen_names[0]])
    for nm in chosen_names[1:]:
        item_filter &= set(result.dataset.items[nm])
    return _ordered_items(result, item_filter)


def exclusive_items(result: RegionResult, sets: Sequence[str]) -> list[str]:
    """Items in EXACTLY this combination — in every set in ``sets``, in none of the others.

    Parameters
    ----------
    result : RegionResult
    sets : sequence of str

    Returns
    -------
    list[str]
        Item identifiers in exactly this combination, ordered by
        ``dataset.item_order``. Empty list if no item qualifies.
    """
    indices = _resolve_set_indices(result, sets)
    mask = _indices_to_mask(indices)
    region = result.regions.get(mask)
    if region is None:
        return []
    return _ordered_items(result, set(region.exclusive_items))


def union_items(result: RegionResult, sets: Sequence[str]) -> list[str]:
    """Items in ANY of the named sets (deduplicated).

    Returns items ordered by ``dataset.item_order``.
    """
    indices = _resolve_set_indices(result, sets)
    set_names = list(result.dataset.set_names)
    chosen_names = [set_names[i] for i in indices]
    item_filter: set[str] = set()
    for nm in chosen_names:
        item_filter |= set(result.dataset.items[nm])
    return _ordered_items(result, item_filter)
