"""Private engines for ``render_venn_svg``'s ``show_items`` and ``highlight``.

The item-text engine (:func:`_render_items_in_regions`) replaces each
region's ``Count_<label>`` text node with a series of ``<tspan>``
children (one per item, optionally column-paginated, optionally
truncated when the region holds more items than
``max_items_per_region``).

The highlight engine (:func:`_apply_highlight`) walks
``Shape*``/``Shape*2`` nodes and rewrites inline ``fill:`` styles:
regions that contribute to at least one highlighted region keep their
colour, all others are desaturated.

Both helpers operate in place on the same lxml-parsed root used by
:func:`render_venn_svg`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from lxml import etree

if TYPE_CHECKING:
    from venn_diagram_lab.analysis import RegionResult

_LETTERS = "ABCDEFGHI"
_SVG_NS = "{http://www.w3.org/2000/svg}"

# Item-text rendering defaults.
_ITEMS_DEFAULTS: dict[str, Any] = {
    "max_items_per_region": 20,
    "ncol_items": 1,
    "truncate_long_names": 12,
    "line_height": 10,
    "font_size": 8,
    "show_counts_with_items": False,
    "ellipsis": "...",
}

# Highlight engine constants.
_HIGHLIGHT_GREY = "#cccccc"
_HIGHLIGHT_OPACITY = "0.25"

_FILL_RE = re.compile(r"fill:\s*#[0-9A-Fa-f]{3,6}")
_OPACITY_RE = re.compile(r"opacity:\s*[0-9.]+")


def _resolve_item_options(user_opts: Mapping[str, Any] | None) -> dict[str, Any]:
    """Merge user-supplied options with defaults; warn on unknown keys."""
    if user_opts is None:
        return dict(_ITEMS_DEFAULTS)
    if not isinstance(user_opts, Mapping):
        raise ValueError("`item_options` must be a mapping or None.")
    unknown = set(user_opts) - set(_ITEMS_DEFAULTS)
    if unknown:
        import warnings  # noqa: PLC0415
        warnings.warn(
            f"Ignoring unknown item_options: {sorted(unknown)!r}",
            UserWarning,
            stacklevel=3,
        )
    out = dict(_ITEMS_DEFAULTS)
    for k, v in user_opts.items():
        if k in _ITEMS_DEFAULTS:
            out[k] = v
    return out


def _truncate_item(s: str, max_chars: int, ellipsis: str) -> str:
    if max_chars <= 0 or len(s) <= max_chars:
        return s
    return s[:max_chars] + ellipsis


def _layout_items_columns(items: Sequence[str], ncol: int) -> list[list[str]]:
    """Lay items out into ``ncol`` columns by row-major order. Pad with ''."""
    if ncol <= 1:
        return [[it] for it in items]
    n = len(items)
    n_rows = (n + ncol - 1) // ncol
    rows: list[list[str]] = []
    for r in range(n_rows):
        start = r * ncol
        end = min(start + ncol, n)
        cells = list(items[start:end])
        while len(cells) < ncol:
            cells.append("")
        rows.append(cells)
    return rows


def _build_region_tspans(
    items: list[str], count: int, opts: dict[str, Any]
) -> list[etree._Element]:
    """Build the <tspan> children for one region's Count_* text node."""
    max_n = int(opts["max_items_per_region"])
    items_to_show = items[:max_n]
    truncated_n = len(items) - len(items_to_show)
    items_to_show = [
        _truncate_item(it, int(opts["truncate_long_names"]), str(opts["ellipsis"]))
        for it in items_to_show
    ]
    rows = _layout_items_columns(items_to_show, int(opts["ncol_items"]))
    line_height = int(opts["line_height"])

    children: list[etree._Element] = []
    if bool(opts["show_counts_with_items"]):
        ts = etree.SubElement(etree.Element(f"{_SVG_NS}wrap"), f"{_SVG_NS}tspan")
        ts.set("x", "0")
        ts.set("dy", "0")
        ts.set("font-weight", "bold")
        ts.text = str(count)
        children.append(ts)
        first_dy = line_height
    else:
        first_dy = 0

    for i, row in enumerate(rows):
        ts = etree.SubElement(etree.Element(f"{_SVG_NS}wrap"), f"{_SVG_NS}tspan")
        ts.set("x", "0")
        if i == 0 and not children:
            ts.set("dy", str(first_dy))
        else:
            ts.set("dy", str(line_height))
        ts.text = "  ".join(row)
        children.append(ts)

    if truncated_n > 0:
        ts = etree.SubElement(etree.Element(f"{_SVG_NS}wrap"), f"{_SVG_NS}tspan")
        ts.set("x", "0")
        ts.set("dy", str(line_height))
        ts.set("font-style", "italic")
        ts.text = f"+{truncated_n} more"
        children.append(ts)
    return children


def _find_count_element(root: etree._Element, count_id: str) -> etree._Element | None:
    """Find an element by id, namespace-agnostic."""
    for el in root.iter():
        if el.get("id") == count_id:
            return el
    return None


def _replace_count_with_items(
    root: etree._Element,
    count_id: str,
    items: list[str],
    count: int,
    opts: dict[str, Any],
) -> None:
    el = _find_count_element(root, count_id)
    if el is None:
        return
    # Drop existing content + children.
    el.text = None
    for child in list(el):
        el.remove(child)
    # Inject the new tspans.
    for ts in _build_region_tspans(items, count, opts):
        el.append(ts)
    el.set("font-size", str(opts["font_size"]))


def _render_items_in_regions(
    root: etree._Element,
    result: RegionResult,
    item_options: Mapping[str, Any] | None,
) -> None:
    """Replace per-region count text with item-name tspans."""
    opts = _resolve_item_options(item_options)
    for region in result.regions.values():
        items = sorted(region.exclusive_items)
        count_id = f"Count_{region.label}"
        if not items:
            el = _find_count_element(root, count_id)
            if el is not None:
                el.text = ""
                for child in list(el):
                    el.remove(child)
            continue
        _replace_count_with_items(root, count_id, items, len(items), opts)


# ---- Highlight engine ------------------------------------------------------


def _resolve_highlight_labels(
    highlight: Sequence[str] | Sequence[int],
    result: RegionResult,
) -> list[str]:
    """Convert highlight= argument into a list of canonical region labels.

    Accepts:
      * sequence of str labels (validated against the full bitmask universe)
      * sequence of int bitmasks (validated against 1..2^n - 1)
    """
    if highlight is None:
        return []
    n = len(result.dataset.set_names)
    letters = _LETTERS[:n]
    max_mask = (1 << n) - 1

    def mask_to_label(m: int) -> str:
        bits = [letters[i] for i in range(n) if m & (1 << i)]
        return "".join(bits)

    seq = list(highlight)
    if not seq:
        return []
    first = seq[0]
    if isinstance(first, bool):
        raise ValueError(
            "`highlight` must be None, a sequence of region labels (str), "
            "or a sequence of region bitmasks (int)."
        )
    if isinstance(first, int):
        labels: list[str] = []
        for m in seq:
            if not isinstance(m, int):
                raise ValueError(
                    "`highlight` mixes int and non-int values."
                )
            if m < 1 or m > max_mask:
                raise ValueError(f"highlight: no region with mask {m}")
            labels.append(mask_to_label(m))
        return labels
    if isinstance(first, str):
        all_labels = {mask_to_label(m) for m in range(1, max_mask + 1)}
        str_labels: list[str] = []
        for lbl in seq:
            if not isinstance(lbl, str):
                raise ValueError("`highlight` mixes str and non-str values.")
            if lbl not in all_labels:
                raise ValueError(f"highlight: unknown region label(s): {lbl!r}")
            str_labels.append(lbl)
        return str_labels
    raise ValueError(
        "`highlight` must be None, a sequence of region labels (str), "
        "or a sequence of region bitmasks (int)."
    )


def _apply_highlight(
    root: etree._Element,
    result: RegionResult,
    highlight: Sequence[str] | Sequence[int] | None,
) -> None:
    """Desaturate Shape* nodes for sets that do not contribute to highlighted regions."""
    if highlight is None:
        return
    labels = _resolve_highlight_labels(highlight, result)
    if not labels:
        return
    n = len(result.dataset.set_names)
    letters = _LETTERS[:n]

    def label_to_mask(lbl: str) -> int:
        m = 0
        for ch in lbl:
            m |= 1 << letters.index(ch)
        return m

    union_mask = 0
    for lbl in labels:
        union_mask |= label_to_mask(lbl)

    # Any set whose bit is NOT in union_mask gets desaturated.
    for i in range(n):
        bit = 1 << i
        if union_mask & bit:
            continue
        letter = letters[i]
        for shape_id in (f"Shape{letter}", f"Shape{letter}2"):
            el = _find_count_element(root, shape_id)
            if el is None:
                continue
            style = el.get("style") or ""
            if not style:
                continue
            new_style = _FILL_RE.sub(f"fill:{_HIGHLIGHT_GREY}", style)
            if "opacity:" in new_style:
                new_style = _OPACITY_RE.sub(
                    f"opacity:{_HIGHLIGHT_OPACITY}", new_style
                )
            else:
                new_style = new_style + f";opacity:{_HIGHLIGHT_OPACITY}"
            el.set("style", new_style)
