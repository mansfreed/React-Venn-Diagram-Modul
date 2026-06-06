"""Cross-feature integration tests for the four Phase 11 additions."""

from __future__ import annotations

import re

from venn_diagram_lab import (
    Dataset,
    analyze,
    exclusive_items,
    parse_region_expression,
    render_venn_svg,
)


def _toy_4set():
    ds = Dataset(
        set_names=["A", "B", "C", "D"],
        items={
            "A": {"g1", "g2", "g3"},
            "B": {"g2", "g3", "g4"},
            "C": {"g3", "g4", "g5"},
            "D": {"g4", "g5", "g6"},
        },
        source_path=None,
        format="csv",
        item_order=("g1", "g2", "g3", "g4", "g5", "g6"),
        universe_size=100,
    )
    return analyze(ds)


def test_dsl_output_composes_with_render_venn_svg_highlight():
    res = _toy_4set()
    # "A & B & C & ~D" -> mask 7 only. D should be desaturated.
    masks = parse_region_expression("A & B & C & ~D", n_sets=4)
    assert len(masks) > 0
    svg = render_venn_svg(res, highlight=masks).svg
    assert re.search(r'id="ShapeD"[^>]*style="[^"]*fill:#cccccc', svg)
    assert not re.search(r'id="ShapeA"[^>]*style="[^"]*fill:#cccccc', svg)


def test_accessors_agree_with_dsl_on_exact_combination():
    res = _toy_4set()
    # g2 is in A and B (not C, not D) => exclusive to {A,B}.
    excl_ab = exclusive_items(res, ["A", "B"])
    assert excl_ab == ["g2"]

    # "A & B & ~C & ~D" resolves to mask 3 (A & B, none of C or D).
    masks = parse_region_expression("A & B & ~C & ~D", n_sets=4)
    assert masks == [3]

    # The region at that mask contains exactly the items returned by the accessor.
    assert sorted(res.regions[3].exclusive_items) == sorted(excl_ab)


def test_show_items_and_highlight_compose():
    res = _toy_4set()
    svg = render_venn_svg(
        res,
        show_items=True,
        highlight=parse_region_expression("A & B & ~C & ~D", n_sets=4),
    ).svg
    assert re.search(r"<[^>]*tspan[^>]*>g[1-6]", svg)
    assert re.search(r'id="Shape[CD]"[^>]*style="[^"]*fill:#cccccc', svg)
