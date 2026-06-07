"""Matplotlib-native Venn renderer for 2/3/4-set classic models + proportional.

The four bundled classic models (``venn-2-set``, ``venn-3-set``,
``venn-4-set``, plus the analytical ``proportional`` solver) map cleanly
to matplotlib primitives: circles for 2/3-set + proportional, tilted
ellipses for the classic 4-set Venn (Venn 1880). Higher set counts (5+
classic, Edwards, Anderson, Mamakani, etc.) use SVG paths that do not
map cleanly to matplotlib primitives -- those models are not supported
here; ``render_venn_svg`` remains the canonical surface for them.

When ``ax`` is provided the function draws into it and returns the
parent ``Figure``; when ``ax`` is None, the function creates its own
``fig, ax = plt.subplots()``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse

from venn_diagram_lab.errors import IncompatibleModelError
from venn_diagram_lab.render.image import MplImage

if TYPE_CHECKING:
    from collections.abc import Mapping

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from venn_diagram_lab.analysis import RegionResult

__all__ = ["render_venn_mpl"]

_DEFAULT_COLORS: dict[str, str] = {
    "A": "#FFF200",
    "B": "#2E3192",
    "C": "#ED1C24",
    "D": "#808285",
}

_POS_2SET: dict[str, tuple[float, float, float]] = {
    "A": (-0.4, 0.0, 0.7),
    "B": (0.4, 0.0, 0.7),
}
_POS_3SET: dict[str, tuple[float, float, float]] = {
    "A": (-0.4, 0.25, 0.65),
    "B": (0.4, 0.25, 0.65),
    "C": (0.0, -0.4, 0.65),
}
_POS_4SET: dict[str, tuple[float, float, float, float, float]] = {
    "A": (-0.35, 0.10, 1.50, 0.85, 45.0),
    "B": (0.10, 0.35, 1.50, 0.85, -45.0),
    "C": (-0.10, -0.35, 1.50, 0.85, 45.0),
    "D": (0.35, -0.10, 1.50, 0.85, -45.0),
}

_NAME_POS_2SET: dict[str, tuple[float, float]] = {"A": (-0.8, 0.85), "B": (0.8, 0.85)}
_NAME_POS_3SET: dict[str, tuple[float, float]] = {
    "A": (-0.8, 1.0),
    "B": (0.8, 1.0),
    "C": (0.0, -1.15),
}
_NAME_POS_4SET: dict[str, tuple[float, float]] = {
    "A": (-1.15, 0.85),
    "B": (1.15, 0.85),
    "C": (-1.15, -0.85),
    "D": (1.15, -0.85),
}

_COUNT_POS_2SET: dict[int, tuple[float, float]] = {
    1: (-0.7, 0.0),
    2: (0.7, 0.0),
    3: (0.0, 0.0),
}
_COUNT_POS_3SET: dict[int, tuple[float, float]] = {
    1: (-0.7, 0.55),
    2: (0.7, 0.55),
    3: (0.0, 0.55),
    4: (0.0, -0.65),
    5: (-0.45, -0.2),
    6: (0.45, -0.2),
    7: (0.0, -0.05),
}
_PROPORTIONAL_2SET = 2
_PROPORTIONAL_3SET = 3

_COUNT_POS_4SET: dict[int, tuple[float, float]] = {
    1: (-0.85, 0.45),
    2: (0.85, 0.45),
    4: (-0.85, -0.45),
    8: (0.85, -0.45),
    3: (0.0, 0.65),
    5: (-0.7, 0.0),
    9: (-0.4, 0.45),
    6: (0.4, 0.45),
    10: (0.7, 0.0),
    12: (0.0, -0.65),
    7: (-0.3, 0.25),
    11: (0.3, 0.25),
    13: (-0.3, -0.25),
    14: (0.3, -0.25),
    15: (0.0, 0.0),
}


def _setup_axes(ax: Axes | None) -> tuple[Figure, Axes]:
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 7))
        return fig, ax
    return ax.figure, ax  # type: ignore[return-value]


def _finalise_axes(ax: Axes, title: str | None) -> None:
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.set_axis_off()
    if title is not None:
        ax.set_title(title, fontsize=12)


def _draw_2set(
    ax: Axes,
    result: RegionResult,
    set_names: list[str],
    colors: dict[str, str],
    show_names: bool,
    show_counts: bool,
    alpha: float,
) -> None:
    for letter in ("A", "B"):
        cx, cy, r = _POS_2SET[letter]
        ax.add_patch(
            Circle(
                (cx, cy), r,
                alpha=alpha,
                facecolor=colors[letter],
                edgecolor="black",
                linewidth=1.2,
            )
        )
        if show_names:
            nx, ny = _NAME_POS_2SET[letter]
            ax.text(
                nx, ny, set_names[ord(letter) - ord("A")],
                ha="center", va="bottom", fontsize=11, fontweight="bold",
            )
    if show_counts:
        for mask, (tx, ty) in _COUNT_POS_2SET.items():
            region = result.regions.get(mask)
            count = region.exclusive_count if region is not None else 0
            ax.text(tx, ty, str(count), ha="center", va="center", fontsize=13)


def _draw_3set(
    ax: Axes,
    result: RegionResult,
    set_names: list[str],
    colors: dict[str, str],
    show_names: bool,
    show_counts: bool,
    alpha: float,
) -> None:
    for letter in ("A", "B", "C"):
        cx, cy, r = _POS_3SET[letter]
        ax.add_patch(
            Circle(
                (cx, cy), r,
                alpha=alpha,
                facecolor=colors[letter],
                edgecolor="black",
                linewidth=1.2,
            )
        )
        if show_names:
            nx, ny = _NAME_POS_3SET[letter]
            va = "bottom" if ny > 0 else "top"
            ax.text(
                nx, ny, set_names[ord(letter) - ord("A")],
                ha="center", va=va, fontsize=11, fontweight="bold",
            )
    if show_counts:
        for mask, (tx, ty) in _COUNT_POS_3SET.items():
            region = result.regions.get(mask)
            count = region.exclusive_count if region is not None else 0
            ax.text(tx, ty, str(count), ha="center", va="center", fontsize=13)


def _draw_4set(
    ax: Axes,
    result: RegionResult,
    set_names: list[str],
    colors: dict[str, str],
    show_names: bool,
    show_counts: bool,
    alpha: float,
) -> None:
    for letter in ("A", "B", "C", "D"):
        cx, cy, w, h, angle = _POS_4SET[letter]
        ax.add_patch(
            Ellipse(
                (cx, cy),
                width=w, height=h, angle=angle,
                alpha=alpha,
                facecolor=colors[letter],
                edgecolor="black",
                linewidth=1.0,
            )
        )
        if show_names:
            nx, ny = _NAME_POS_4SET[letter]
            ax.text(
                nx, ny, set_names[ord(letter) - ord("A")],
                ha="center", va="center", fontsize=11, fontweight="bold",
            )
    if show_counts:
        for mask, (tx, ty) in _COUNT_POS_4SET.items():
            region = result.regions.get(mask)
            count = region.exclusive_count if region is not None else 0
            ax.text(tx, ty, str(count), ha="center", va="center", fontsize=11)


def _draw_proportional(
    ax: Axes,
    result: RegionResult,
    set_names: list[str],
    colors: dict[str, str],
    show_names: bool,
    show_counts: bool,
    alpha: float,
) -> None:
    from venn_diagram_lab.proportional import solve_2set, solve_3set  # noqa: PLC0415

    n = len(set_names)
    if n == _PROPORTIONAL_2SET:
        a_only = result.regions.get(1)
        b_only = result.regions.get(2)
        ab = result.regions.get(3)
        layout = solve_2set(
            a_only.exclusive_count if a_only else 0,
            b_only.exclusive_count if b_only else 0,
            ab.exclusive_count if ab else 0,
        )
    elif n == _PROPORTIONAL_3SET:
        regions = {
            mask: (region.exclusive_count if region is not None else 0)
            for mask, region in result.regions.items()
        }
        for mask in range(1, 8):
            regions.setdefault(mask, 0)
        layout = solve_3set(regions)
    else:
        raise IncompatibleModelError(
            f"model='proportional' supports 2 or 3 sets only (got {n}). "
            "Use render_venn_svg for higher set counts.",
        )

    letters = ("A", "B", "C")[:n]
    for letter, circle in zip(letters, layout.circles, strict=False):
        ax.add_patch(
            Circle(
                (circle.cx, circle.cy), circle.r,
                alpha=alpha,
                facecolor=colors[letter],
                edgecolor="black",
                linewidth=1.2,
            )
        )
        if show_names:
            ax.text(
                circle.cx,
                circle.cy + circle.r + 0.05,
                set_names[ord(letter) - ord("A")],
                ha="center", va="bottom", fontsize=11, fontweight="bold",
            )
    if show_counts:
        for letter, circle in zip(letters, layout.circles, strict=False):
            mask = 1 << (ord(letter) - ord("A"))
            region = result.regions.get(mask)
            ax.text(
                circle.cx, circle.cy,
                str(region.exclusive_count if region else 0),
                ha="center", va="center", fontsize=12,
            )

    if layout.circles:
        xs = [c.cx for c in layout.circles]
        ys = [c.cy for c in layout.circles]
        rs = [c.r for c in layout.circles]
        pad = max(rs) + 0.2
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.set_aspect("equal")
        ax.set_axis_off()


def render_venn_mpl(
    result: RegionResult,
    *,
    ax: Axes | None = None,
    model: str | None = None,
    set_names: list[str] | None = None,
    colors: Mapping[str, str] | None = None,
    title: str | None = None,
    show_names: bool = True,
    show_counts: bool = True,
    alpha: float = 0.45,
) -> MplImage:
    """Render a Venn diagram on a matplotlib Axes.

    Supports the 2-set, 3-set, and 4-set classic models plus the
    analytical ``proportional`` model (2 or 3 sets). Higher set counts
    or template-based models (Edwards, Anderson, Mamakani, ...) raise
    ``IncompatibleModelError`` with a pointer at ``render_venn_svg``.

    Parameters
    ----------
    result : RegionResult from :func:`venn_diagram_lab.analyze`.
    ax : optional matplotlib Axes to draw into. When None, a 7x7 figure
        is created internally.
    model : 'venn-2-set' / 'venn-3-set' / 'venn-4-set' / 'proportional'.
        When None, picks the canonical classic model for the dataset's
        set count.
    set_names : per-set display name override. Defaults to
        ``result.dataset.set_names``.
    colors : per-letter (A..D) fill color override.
    title : optional title above the diagram.
    show_names : draw the set names. Default True.
    show_counts : draw the per-region exclusive counts. Default True.
    alpha : circle/ellipse fill alpha (0..1). Default 0.45.
    """
    n = len(result.dataset.set_names)
    chosen_model = model if model is not None else result.model
    if chosen_model in (None, "auto"):
        chosen_model = f"venn-{n}-set"

    supported_classic = {"venn-2-set", "venn-3-set", "venn-4-set"}
    if chosen_model not in supported_classic and chosen_model != "proportional":
        raise IncompatibleModelError(
            f"render_venn_mpl supports only venn-2-set / venn-3-set / "
            f"venn-4-set / proportional (got {chosen_model!r}). Use "
            "render_venn_svg for template-based models or higher set counts.",
        )
    if chosen_model in supported_classic and n not in {2, 3, 4}:
        raise IncompatibleModelError(
            f"render_venn_mpl classic models require 2..4 sets (dataset "
            f"has {n}). Use render_venn_svg for higher set counts.",
        )

    fig, ax_used = _setup_axes(ax)
    display_names = list(set_names) if set_names is not None else list(result.dataset.set_names)
    palette = dict(_DEFAULT_COLORS)
    if colors:
        palette.update(colors)

    if chosen_model == "proportional":
        _draw_proportional(
            ax_used, result, display_names, palette,
            show_names, show_counts, alpha,
        )
        if title is not None:
            ax_used.set_title(title, fontsize=12)
    elif chosen_model == "venn-2-set":
        _draw_2set(
            ax_used, result, display_names, palette,
            show_names, show_counts, alpha,
        )
        _finalise_axes(ax_used, title)
    elif chosen_model == "venn-3-set":
        _draw_3set(
            ax_used, result, display_names, palette,
            show_names, show_counts, alpha,
        )
        _finalise_axes(ax_used, title)
    elif chosen_model == "venn-4-set":
        _draw_4set(
            ax_used, result, display_names, palette,
            show_names, show_counts, alpha,
        )
        _finalise_axes(ax_used, title)

    legend = {chr(ord("A") + i): display_names[i] for i in range(n)}
    return MplImage(fig=fig, legend=legend)
