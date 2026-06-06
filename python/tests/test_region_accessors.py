"""Tests for the region-accessor sugar (Phase 11 — Feature C)."""

from __future__ import annotations

import pytest

from venn_diagram_lab import (
    Dataset,
    analyze,
    exclusive_items,
    intersection_items,
    union_items,
)


def _toy_3set():
    """3-set toy: A = {x, y}, B = {y, z}, C = {z, w}.

    Expected memberships:
      x in A only
      y in A and B
      z in B and C
      w in C only
    """
    ds = Dataset(
        set_names=["A", "B", "C"],
        items={"A": {"x", "y"}, "B": {"y", "z"}, "C": {"z", "w"}},
        source_path=None,
        format="csv",
        item_order=("x", "y", "z", "w"),
        universe_size=10,
    )
    return analyze(ds)


def test_intersection_items_returns_items_in_every_named_set():
    res = _toy_3set()
    assert sorted(intersection_items(res, ["A", "B"])) == ["y"]
    assert sorted(intersection_items(res, ["B", "C"])) == ["z"]
    assert intersection_items(res, ["A", "C"]) == []


def test_intersection_items_accepts_display_names():
    res = _toy_3set()  # set_names ARE "A", "B", "C" here
    assert sorted(intersection_items(res, ["A"])) == ["x", "y"]


def test_exclusive_items_returns_items_in_exactly_this_combination():
    res = _toy_3set()
    # x in A only => exclusive to {A}
    assert exclusive_items(res, ["A"]) == ["x"]
    # y in A and B (not C) => exclusive to {A, B}
    assert exclusive_items(res, ["A", "B"]) == ["y"]
    # z in B and C (not A) => exclusive to {B, C}
    assert exclusive_items(res, ["B", "C"]) == ["z"]
    # No item is exclusively in {A, C}
    assert exclusive_items(res, ["A", "C"]) == []


def test_union_items_returns_items_in_any_named_set():
    res = _toy_3set()
    assert sorted(union_items(res, ["A", "B"])) == ["x", "y", "z"]
    assert sorted(union_items(res, ["A", "B", "C"])) == ["w", "x", "y", "z"]
    assert sorted(union_items(res, ["A"])) == ["x", "y"]


def test_accessors_reject_unknown_set_identifiers():
    res = _toy_3set()
    with pytest.raises(ValueError, match="Unknown set"):
        intersection_items(res, ["A", "Z"])
    with pytest.raises(ValueError, match="Unknown set"):
        exclusive_items(res, ["Q"])
    with pytest.raises(ValueError, match="Unknown set"):
        union_items(res, ["A", "B", "X"])


def test_accessors_reject_empty_sets():
    res = _toy_3set()
    with pytest.raises(ValueError, match="at least one set"):
        intersection_items(res, [])
    with pytest.raises(ValueError, match="at least one set"):
        exclusive_items(res, [])
    with pytest.raises(ValueError, match="at least one set"):
        union_items(res, [])


def test_accessors_preserve_item_order():
    """Output ordering follows dataset.item_order for deterministic parity."""
    res = _toy_3set()
    # item_order is ("x", "y", "z", "w") in that order; intersection of A is "x", "y".
    assert intersection_items(res, ["A"]) == ["x", "y"]
    # Union A | B | C in item_order: x (in A), y (in A,B), z (in B,C), w (in C).
    assert union_items(res, ["A", "B", "C"]) == ["x", "y", "z", "w"]
