"""Matplotlib variant of the cluster-ordered Jaccard heatmap.

Same input contract as :func:`render_cluster_heatmap_svg`: a
:class:`~venn_diagram_lab.analysis.RegionResult` is reordered by
hierarchical clustering on ``1 - Jaccard`` distance; the matplotlib
variant uses ``scipy.cluster.hierarchy.dendrogram`` for the side bands
and ``imshow`` for the heatmap, plus a colorbar.

The SVG variant is unchanged so the webtool byte-equivalent contract is
preserved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import linkage as _scipy_linkage
from scipy.spatial.distance import squareform

from venn_diagram_lab.render.image import MplImage

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from venn_diagram_lab.analysis import RegionResult

__all__ = ["render_cluster_heatmap_mpl"]

_MIN_SETS = 2
_HEAT_TEXT_DARK_THRESHOLD = 0.55


def _draw_single_panel(
    ax: Axes,
    jaccard_arr: np.ndarray,
    set_names: list[str],
    letters: list[str],
    cmap: str,
    n: int,
) -> MplImage:
    fig = ax.figure
    order = list(range(n))
    reordered = jaccard_arr[np.ix_(order, order)]
    ax.imshow(reordered, cmap=cmap, vmin=0, vmax=1, aspect="equal")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    labels = [f"{set_names[i]} ({letters[i]})" for i in order]
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    for i in range(n):
        for j in range(n):
            v = reordered[i, j]
            ax.text(
                j, i, f"{v:.2f}",
                ha="center", va="center",
                color="white" if v > _HEAT_TEXT_DARK_THRESHOLD else "#222",
                fontsize=8,
            )
    ax.set_title("Jaccard similarity")
    legend = {letters[i]: set_names[i] for i in range(n)}
    return MplImage(fig=fig, legend=legend)  # type: ignore[arg-type]


def _draw_multi_panel(
    linkage_z: np.ndarray,
    jaccard_arr: np.ndarray,
    set_names: list[str],
    letters: list[str],
    cmap: str,
    n: int,
    show_row_dendrogram: bool,
    show_col_dendrogram: bool,
) -> MplImage:
    fig = plt.figure(figsize=(7, 6))
    gs = fig.add_gridspec(
        2, 3,
        width_ratios=[1, 4, 0.2],
        height_ratios=[1, 4],
        wspace=0.02, hspace=0.02,
    )

    ax_top = fig.add_subplot(gs[0, 1])
    ax_left = fig.add_subplot(gs[1, 0])
    ax_heat = fig.add_subplot(gs[1, 1])
    ax_cbar = fig.add_subplot(gs[1, 2])

    if show_col_dendrogram:
        ddata_top = dendrogram(
            linkage_z, no_plot=False, ax=ax_top, color_threshold=0,
            above_threshold_color="#555555", no_labels=True,
            orientation="top",
        )
        order = list(map(int, ddata_top["leaves"]))
    else:
        order = list(range(n))
    ax_top.set_axis_off()

    if show_row_dendrogram:
        dendrogram(
            linkage_z, no_plot=False, ax=ax_left, color_threshold=0,
            above_threshold_color="#555555", no_labels=True,
            orientation="left",
        )
    ax_left.set_axis_off()

    reordered = jaccard_arr[np.ix_(order, order)]
    im = ax_heat.imshow(reordered, cmap=cmap, vmin=0, vmax=1, aspect="equal")
    labels = [f"{set_names[i]} ({letters[i]})" for i in order]
    ax_heat.set_xticks(range(n))
    ax_heat.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax_heat.set_yticks(range(n))
    ax_heat.set_yticklabels(labels, fontsize=8)
    for i in range(n):
        for j in range(n):
            v = reordered[i, j]
            ax_heat.text(
                j, i, f"{v:.2f}",
                ha="center", va="center",
                color="white" if v > _HEAT_TEXT_DARK_THRESHOLD else "#222",
                fontsize=7,
            )
    ax_heat.set_title("Jaccard similarity")
    fig.colorbar(im, cax=ax_cbar)

    legend = {letters[i]: set_names[i] for i in range(n)}
    return MplImage(fig=fig, legend=legend)


def render_cluster_heatmap_mpl(
    result: RegionResult,
    *,
    ax: Axes | None = None,
    linkage: str = "average",
    show_row_dendrogram: bool = True,
    show_col_dendrogram: bool = True,
    cmap: str = "Blues",
) -> MplImage:
    """Render a cluster-ordered Jaccard heatmap on matplotlib.

    Parameters
    ----------
    result : RegionResult.
    ax : optional Axes for the heatmap panel. When None, a 7x6 figure
        is created with side bands for the dendrograms + a colorbar.
        When supplied, dendrograms are NOT drawn (single-axes mode).
    linkage : one of 'average' (UPGMA), 'complete', 'single'.
    show_row_dendrogram, show_col_dendrogram : draw the left/top
        dendrogram. Ignored when ``ax`` is supplied.
    cmap : matplotlib colormap name. Default 'Blues' matches the
        white -> dark blue gradient of the SVG variant.
    """
    set_names = list(result.dataset.set_names)
    n = len(set_names)
    letters = [chr(ord("A") + i) for i in range(n)]

    if n < _MIN_SETS:
        msg = "Cluster heatmap requires at least 2 sets."
        raise ValueError(msg)

    jaccard_arr = np.asarray(result.statistics.jaccard.to_numpy(), dtype=float)
    distance = 1.0 - jaccard_arr
    np.fill_diagonal(distance, 0.0)
    condensed = squareform(distance, checks=False)
    linkage_z = _scipy_linkage(condensed, method=linkage)

    if ax is not None:
        return _draw_single_panel(ax, jaccard_arr, set_names, letters, cmap, n)

    return _draw_multi_panel(
        linkage_z, jaccard_arr, set_names, letters, cmap, n,
        show_row_dendrogram, show_col_dendrogram,
    )
