"""Tests for the show_items + item_options path in render_venn_svg."""

from __future__ import annotations

import pytest

from venn_diagram_lab import Dataset, analyze, render_venn_svg


def _toy_3set():
    ds = Dataset(
        set_names=["A", "B", "C"],
        items={"A": {"x", "y"}, "B": {"y", "z"}, "C": {"z", "w"}},
        source_path=None,
        format="csv",
        item_order=("x", "y", "z", "w"),
        universe_size=10,
    )
    return analyze(ds)


def test_show_items_false_is_identical_to_default():
    res = _toy_3set()
    svg_default = render_venn_svg(res).svg
    svg_explicit = render_venn_svg(res, show_items=False).svg
    assert svg_default == svg_explicit


def test_show_items_true_replaces_counts_with_item_tspans():
    res = _toy_3set()
    svg = render_venn_svg(res, show_items=True).svg
    # Each item should appear inside a tspan somewhere.
    for item in ("x", "y", "z", "w"):
        assert f">{item}<" in svg or f"  {item}" in svg, (
            f"item {item} missing from svg"
        )


def test_show_items_truncate_long_names():
    ds = Dataset(
        set_names=["A", "B"],
        items={
            "A": {"verylongitemname_aaaaaaa"},
            "B": {"verylongitemname_aaaaaaa"},
        },
        source_path=None,
        format="csv",
        item_order=("verylongitemname_aaaaaaa",),
        universe_size=10,
    )
    res = analyze(ds)
    svg = render_venn_svg(
        res, show_items=True, item_options={"truncate_long_names": 8}
    ).svg
    assert "verylong..." in svg


def test_show_items_max_items_per_region_overflow():
    items = {f"g{i}" for i in range(30)}
    ds = Dataset(
        set_names=["A", "B"],
        items={"A": items, "B": items},
        source_path=None,
        format="csv",
        item_order=tuple(f"g{i}" for i in range(30)),
        universe_size=100,
    )
    res = analyze(ds)
    svg = render_venn_svg(
        res, show_items=True, item_options={"max_items_per_region": 5}
    ).svg
    assert "+25 more" in svg


def test_show_items_unknown_option_warns():
    res = _toy_3set()
    with pytest.warns(UserWarning, match="Ignoring unknown item_options"):
        render_venn_svg(res, show_items=True, item_options={"bogus_key": 99})
