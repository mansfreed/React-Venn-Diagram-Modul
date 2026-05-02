"""MplImage: matplotlib Figure container with save + Jupyter helpers."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


@dataclass(frozen=True)
class MplImage:
    """Matplotlib figure emitted by :func:`render_upset` and :func:`render_network`.

    Sibling to ``SvgImage``, which wraps an SVG string. Both share the ``save(path)``
    convention (format auto-detected from extension) and a Jupyter inline-render hook.

    Attributes:
        fig: The underlying :class:`matplotlib.figure.Figure`.

    Methods:
        save(path): Write to disk; supports ``.png``, ``.pdf``, ``.svg``.
            Default dpi=300 for publication quality.
    """

    fig: Figure

    def save(self, path: Path | str, *, dpi: int = 300) -> None:
        """Write the figure to disk.

        Format auto-detected from the extension. Supported: .png, .pdf, .svg.
        Default dpi=300 for publication quality (vs. SvgImage's 96 = screen).
        """
        p = Path(path)
        ext = p.suffix.lower()
        if ext not in {".png", ".pdf", ".svg"}:
            raise ValueError(
                f"Unsupported output extension {ext!r}. Use .png, .pdf, or .svg."
            )
        self.fig.savefig(str(p), dpi=dpi, format=ext.lstrip("."))

    def _repr_png_(self) -> bytes:
        """Jupyter inline-render hook (returns PNG bytes)."""
        buf = io.BytesIO()
        self.fig.savefig(buf, format="png", dpi=96)
        return buf.getvalue()
