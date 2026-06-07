"""Tests for render_cluster_heatmap_mpl."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from venn_diagram_lab import (
    Dataset,
    MplImage,
    analyze,
    load_sample,
    render_cluster_heatmap_mpl,
)


def _toy_3set_result():
    ds = Dataset(
        set_names=["A", "B", "C"],
        items={"A": {"x", "y"}, "B": {"y", "z"}, "C": {"z", "w"}},
        source_path=None,
        format="csv",
        item_order=("x", "y", "z", "w"),
        universe_size=10,
    )
    return analyze(ds)


def test_render_cluster_heatmap_mpl_returns_mplimage():
    img = render_cluster_heatmap_mpl(_toy_3set_result())
    assert isinstance(img, MplImage)
    plt.close(img.fig)


def test_render_cluster_heatmap_mpl_has_heatmap_axes():
    img = render_cluster_heatmap_mpl(_toy_3set_result())
    assert len(img.fig.axes) >= 1
    plt.close(img.fig)


def test_render_cluster_heatmap_mpl_with_cancer_drivers_sample():
    res = analyze(load_sample("dataset_real_cancer_drivers_4"))
    img = render_cluster_heatmap_mpl(res, linkage="average")
    assert isinstance(img, MplImage)
    plt.close(img.fig)


def test_render_cluster_heatmap_mpl_accepts_external_axes():
    res = _toy_3set_result()
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    img = render_cluster_heatmap_mpl(res, ax=ax)
    assert img.fig is fig
    plt.close(fig)


@pytest.mark.parametrize("linkage", ["average", "complete", "single"])
def test_render_cluster_heatmap_mpl_supports_linkage_methods(linkage: str):
    res = analyze(load_sample("dataset_real_cancer_drivers_4"))
    img = render_cluster_heatmap_mpl(res, linkage=linkage)
    assert isinstance(img, MplImage)
    plt.close(img.fig)
