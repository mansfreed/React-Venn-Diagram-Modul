"""Tests for the new SVG renderers added in v2.2.2."""

from pathlib import Path

from venn_diagram_lab.analysis import analyze
from venn_diagram_lab.io import load_tsv
from venn_diagram_lab.render.svg import (
    render_cluster_heatmap_svg,
    render_share_distribution_svg,
)

# Fixture has 4 binary set columns (Vogelstein, COSMIC_CGC, OncoKB, IntOGen).
_EXPECTED_SETS = 4

FIXTURE = Path(__file__).resolve().parents[2] / "data" / "dataset_real_cancer_drivers_4.tsv"


def test_render_share_distribution_emits_svg_with_n_bars() -> None:
    ds = load_tsv(FIXTURE, binary=True, prefix_cols=1)
    img = render_share_distribution_svg(ds)
    assert img.content.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    bar_count = img.content.count('class="sd-bar"')
    assert bar_count == _EXPECTED_SETS


def test_render_cluster_heatmap_emits_dendrogram_groups() -> None:
    ds = load_tsv(FIXTURE, binary=True, prefix_cols=1)
    res = analyze(ds)
    img = render_cluster_heatmap_svg(res, linkage="average")
    assert 'class="hm-dendro-col"' in img.content
    assert 'class="hm-dendro-row"' in img.content


def test_render_cluster_heatmap_respects_show_flags() -> None:
    ds = load_tsv(FIXTURE, binary=True, prefix_cols=1)
    res = analyze(ds)
    img = render_cluster_heatmap_svg(
        res, linkage="average", show_row_dendrogram=False, show_col_dendrogram=True
    )
    assert 'class="hm-dendro-col"' in img.content
    assert 'class="hm-dendro-row"' not in img.content
