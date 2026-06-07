"""Tests for render_venn_mpl."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from venn_diagram_lab import (
    Dataset,
    IncompatibleModelError,
    MplImage,
    analyze,
    load_sample,
    render_venn_mpl,
)


def _toy_2set() -> RegionResult:  # type: ignore[name-defined]  # noqa: F821
    ds = Dataset(
        set_names=["A", "B"],
        items={"A": {"x", "y"}, "B": {"y", "z"}},
        source_path=None,
        format="csv",
        item_order=("x", "y", "z"),
        universe_size=10,
    )
    return analyze(ds)


def _toy_3set() -> RegionResult:  # type: ignore[name-defined]  # noqa: F821
    ds = Dataset(
        set_names=["A", "B", "C"],
        items={"A": {"x", "y"}, "B": {"y", "z"}, "C": {"z", "w"}},
        source_path=None,
        format="csv",
        item_order=("x", "y", "z", "w"),
        universe_size=10,
    )
    return analyze(ds)


def _toy_4set() -> RegionResult:  # type: ignore[name-defined]  # noqa: F821
    ds = Dataset(
        set_names=["A", "B", "C", "D"],
        items={
            "A": {"x", "y"},
            "B": {"y", "z"},
            "C": {"z", "w"},
            "D": {"w", "v"},
        },
        source_path=None,
        format="csv",
        item_order=("x", "y", "z", "w", "v"),
        universe_size=10,
    )
    return analyze(ds)


def _toy_5set() -> RegionResult:  # type: ignore[name-defined]  # noqa: F821
    ds = Dataset(
        set_names=["A", "B", "C", "D", "E"],
        items={
            "A": {"a1"},
            "B": {"b1"},
            "C": {"c1"},
            "D": {"d1"},
            "E": {"e1"},
        },
        source_path=None,
        format="csv",
        item_order=("a1", "b1", "c1", "d1", "e1"),
        universe_size=10,
    )
    return analyze(ds)


def test_render_venn_mpl_2set_returns_mplimage():
    res = _toy_2set()
    img = render_venn_mpl(res)
    assert isinstance(img, MplImage)
    assert img.legend == {"A": "A", "B": "B"}
    plt.close(img.fig)


def test_render_venn_mpl_3set_returns_mplimage():
    res = _toy_3set()
    img = render_venn_mpl(res)
    assert isinstance(img, MplImage)
    assert img.legend == {"A": "A", "B": "B", "C": "C"}
    plt.close(img.fig)


def test_render_venn_mpl_4set_returns_mplimage():
    res = _toy_4set()
    img = render_venn_mpl(res)
    assert isinstance(img, MplImage)
    assert img.legend == {"A": "A", "B": "B", "C": "C", "D": "D"}
    plt.close(img.fig)


def test_render_venn_mpl_rejects_5set_with_helpful_message():
    res = _toy_5set()
    with pytest.raises(IncompatibleModelError, match="render_venn_svg"):
        render_venn_mpl(res)


def test_render_venn_mpl_accepts_external_axes():
    res = _toy_3set()
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    img = render_venn_mpl(res, ax=ax[0])
    assert img.fig is fig
    plt.close(fig)


def test_render_venn_mpl_creates_own_figure_when_ax_is_none():
    res = _toy_3set()
    img = render_venn_mpl(res, ax=None)
    assert img.fig is not None
    plt.close(img.fig)


def test_render_venn_mpl_proportional_2set_uses_solver():
    res = _toy_2set()
    img = render_venn_mpl(res, model="proportional")
    assert isinstance(img, MplImage)
    plt.close(img.fig)


def test_render_venn_mpl_proportional_4set_rejects_with_helpful_message():
    res = _toy_4set()
    with pytest.raises(IncompatibleModelError, match="proportional"):
        render_venn_mpl(res, model="proportional")


def test_render_venn_mpl_honors_custom_colors():
    res = _toy_2set()
    img = render_venn_mpl(res, colors={"A": "#FF0000", "B": "#00FF00"})
    ax = img.fig.axes[0]
    patch_colors = [p.get_facecolor() for p in ax.patches]
    assert len(patch_colors) >= 2  # noqa: PLR2004
    plt.close(img.fig)


def test_render_venn_mpl_with_cancer_drivers_sample():
    res = analyze(load_sample("dataset_real_cancer_drivers_4"))
    img = render_venn_mpl(res, title="Cancer drivers (matplotlib)")
    assert isinstance(img, MplImage)
    ax = img.fig.axes[0]
    assert len(ax.patches) == 4  # noqa: PLR2004
    plt.close(img.fig)
