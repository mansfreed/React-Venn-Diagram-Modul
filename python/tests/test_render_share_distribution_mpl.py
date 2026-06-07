"""Tests for render_share_distribution_mpl."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from venn_diagram_lab import (
    Dataset,
    MplImage,
    load_sample,
    render_share_distribution_mpl,
)


def _toy_3set() -> Dataset:
    return Dataset(
        set_names=["A", "B", "C"],
        items={"A": {"x", "y"}, "B": {"y", "z"}, "C": {"z", "w"}},
        source_path=None,
        format="csv",
        item_order=("x", "y", "z", "w"),
        universe_size=10,
    )


def test_render_share_distribution_mpl_returns_mplimage():
    img = render_share_distribution_mpl(_toy_3set())
    assert isinstance(img, MplImage)
    assert img.legend == {}
    plt.close(img.fig)


def test_render_share_distribution_mpl_one_bar_per_k():
    img = render_share_distribution_mpl(_toy_3set())
    ax = img.fig.axes[0]
    bars = list(ax.patches)
    assert len(bars) == 3  # noqa: PLR2004
    plt.close(img.fig)


def test_render_share_distribution_mpl_accepts_external_axes():
    _fig, ax = plt.subplots(1, 2)
    img = render_share_distribution_mpl(_toy_3set(), ax=ax[0])
    assert img.fig is _fig
    plt.close(_fig)


def test_render_share_distribution_mpl_with_cancer_drivers_sample():
    img = render_share_distribution_mpl(load_sample("dataset_real_cancer_drivers_4"))
    ax = img.fig.axes[0]
    assert len(list(ax.patches)) == 4  # noqa: PLR2004
    title_or_xlabel = (ax.get_title() + " " + ax.get_xlabel()).lower()
    assert "share" in title_or_xlabel or "membership" in title_or_xlabel
    plt.close(img.fig)
