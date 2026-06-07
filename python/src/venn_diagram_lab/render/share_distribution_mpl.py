"""Matplotlib variant of the Item Share Distribution histogram.

Same input contract as :func:`render_share_distribution_svg`: a
:class:`~venn_diagram_lab.io.Dataset` whose items are aggregated into N
bars (``k = 1..N``) counting how many items belong to exactly that many
sets. The matplotlib variant adds a proper y-axis with grid lines, an
``ax=`` argument for subplot composition, and the standard
:class:`MplImage` wrapper for consistent in-notebook behaviour.

The SVG variant is unchanged so the webtool byte-equivalent contract is
preserved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from venn_diagram_lab.render.image import MplImage
from venn_diagram_lab.render.svg import _dataset_to_binary_matrix
from venn_diagram_lab.share_distribution import item_share_distribution

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from venn_diagram_lab.io import Dataset

__all__ = ["render_share_distribution_mpl"]

_GRAD_LOW = "#ffe4b5"
_GRAD_HIGH = "#7e14ff"


def render_share_distribution_mpl(
    dataset: Dataset,
    *,
    ax: Axes | None = None,
    color_low: str = _GRAD_LOW,
    color_high: str = _GRAD_HIGH,
) -> MplImage:
    """Render the Item Share Distribution as a matplotlib bar chart.

    Parameters
    ----------
    dataset : Dataset.
    ax : optional Axes to draw into. When None, a 6x4 figure is created.
    color_low, color_high : the tier-gradient endpoints. Defaults match
        the SVG variant.
    """
    matrix = _dataset_to_binary_matrix(dataset)
    dist = item_share_distribution(matrix)
    n = len(dataset.set_names)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure  # type: ignore[assignment]

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "vdl_share", [color_low, color_high],
    )
    ks = list(range(1, n + 1))
    counts = [dist.get(k, 0) for k in ks]
    colors = [cmap(i / (n - 1)) for i in range(n)] if n > 1 else [cmap(0.0)]

    bars = ax.bar(ks, counts, color=colors, edgecolor="#333", linewidth=0.5)
    for bar, count in zip(bars, counts, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(count),
            ha="center", va="bottom", fontsize=9,
        )
    ax.set_xticks(ks)
    ax.set_xticklabels([f"{k} set" if k == 1 else f"{k} sets" for k in ks])
    ax.set_xlabel("Item membership (number of sets)")
    ax.set_ylabel("Items")
    ax.set_title("Item Share Distribution")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    return MplImage(fig=fig, legend={})
