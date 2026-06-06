"""Tests for the highlight spotlight mode in render_venn_svg."""

from __future__ import annotations

import re

import pytest

from venn_diagram_lab import (
    Dataset,
    analyze,
    parse_region_expression,
    render_venn_svg,
)


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


def test_highlight_none_is_identical_to_default():
    res = _toy_3set()
    svg_default = render_venn_svg(res).svg
    svg_null = render_venn_svg(res, highlight=None).svg
    assert svg_default == svg_null


def test_highlight_AB_desaturates_set_C():  # noqa: N802 -- AB/C refer to set letters
    res = _toy_3set()
    svg = render_venn_svg(res, highlight=["AB"]).svg
    assert re.search(r'id="ShapeC"[^>]*style="[^"]*fill:#cccccc', svg)
    assert not re.search(r'id="ShapeA"[^>]*style="[^"]*fill:#cccccc', svg)
    assert not re.search(r'id="ShapeB"[^>]*style="[^"]*fill:#cccccc', svg)


def test_highlight_accepts_bitmask_list():
    res = _toy_3set()
    # Mask 3 = AB, mask 5 = AC. Union covers A, B, C => no desaturation.
    svg = render_venn_svg(res, highlight=[3, 5]).svg
    assert not re.search(r'id="Shape[ABC]"[^>]*style="[^"]*fill:#cccccc', svg)


def test_highlight_composes_with_parse_region_expression():
    res = _toy_3set()
    # "A & B" -> [3, 7]. Union covers A, B, C => no desaturation.
    masks = parse_region_expression("A & B", n_sets=3)
    svg = render_venn_svg(res, highlight=masks).svg
    assert not re.search(r'id="Shape[ABC]"[^>]*style="[^"]*fill:#cccccc', svg)

    # "A & B & ~C" -> [3]. Only A, B contribute => C desaturated.
    masks2 = parse_region_expression("A & B & ~C", n_sets=3)
    svg2 = render_venn_svg(res, highlight=masks2).svg
    assert re.search(r'id="ShapeC"[^>]*style="[^"]*fill:#cccccc', svg2)


def test_highlight_rejects_unknown_label():
    res = _toy_3set()
    with pytest.raises(ValueError, match="unknown region label"):
        render_venn_svg(res, highlight=["XYZ"])


def test_highlight_rejects_unknown_bitmask():
    res = _toy_3set()
    with pytest.raises(ValueError, match="no region with mask"):
        render_venn_svg(res, highlight=[99])


def test_highlight_rejects_type_mismatched_inputs():
    res = _toy_3set()
    with pytest.raises(ValueError, match="must be None"):
        render_venn_svg(res, highlight=[True, False])
