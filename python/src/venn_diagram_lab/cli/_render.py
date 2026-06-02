"""`vdl render ...` subapp — visual outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from venn_diagram_lab.analysis import analyze
from venn_diagram_lab.cli._common import (
    STDOUT_SENTINEL,
    exit_error,
    load_input,
    resolve_out,
    stem_for,
    write_text_out,
)
from venn_diagram_lab.errors import VennDiagramError

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="Render visual outputs (Venn / UpSet / Network / Heatmap / Histogram).",
)


# ---- helpers ---------------------------------------------------------------


def _save_or_stream(img: object, target: Path, dry_run: bool, kind: str) -> None:
    """Common save / stdout-stream / dry-run dispatch."""
    if dry_run:
        typer.echo(f"[dry-run] would write {target}")
        return
    if target is STDOUT_SENTINEL:
        raw = getattr(img, "content", None) or getattr(img, "svg", None) or str(img)
        write_text_out(target, str(raw))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    save = img.save  # type: ignore[attr-defined]
    save(target)
    typer.echo(f"Wrote {target}")


# ---- venn ------------------------------------------------------------------


@app.command("venn")
def cmd_venn(
    input: Annotated[str, typer.Argument(help="Dataset path or bundled sample name")],
    *,
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Output path; default: <stem>__venn.<ext> in CWD"),
    ] = None,
    model: Annotated[str, typer.Option(help="Model name; 'auto' or 'proportional'")] = "auto",
    show_names: Annotated[bool, typer.Option()] = True,
    show_counts: Annotated[bool, typer.Option()] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Render the Venn diagram SVG (or PNG/PDF — format inferred from `--out`)."""
    from venn_diagram_lab.render.svg import render_venn_svg  # noqa: PLC0415
    try:
        ds = load_input(input)
        result = analyze(ds, model=model)
    except (VennDiagramError, OSError) as e:
        exit_error(str(e))
    img = render_venn_svg(result, show_names=show_names, show_counts=show_counts)
    target = resolve_out(out, input, "venn", "svg")
    _save_or_stream(img, target, dry_run, "venn")


# ---- upset -----------------------------------------------------------------


@app.command("upset")
def cmd_upset(
    input: Annotated[str, typer.Argument()],
    *,
    out: Annotated[Path | None, typer.Option("--out", "-o")] = None,
    model: Annotated[str, typer.Option()] = "auto",
    max_columns: Annotated[int, typer.Option(help="Cap visible intersections")] = 20,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Render the UpSet plot SVG."""
    from venn_diagram_lab.render.upset import render_upset  # noqa: PLC0415
    try:
        ds = load_input(input)
        result = analyze(ds, model=model)
    except (VennDiagramError, OSError) as e:
        exit_error(str(e))
    img = render_upset(result, max_columns=max_columns)
    target = resolve_out(out, input, "upset", "svg")
    _save_or_stream(img, target, dry_run, "upset")


# ---- network ---------------------------------------------------------------


@app.command("network")
def cmd_network(
    input: Annotated[str, typer.Argument()],
    *,
    out: Annotated[Path | None, typer.Option("--out", "-o")] = None,
    model: Annotated[str, typer.Option()] = "auto",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Render the Network plot SVG."""
    from venn_diagram_lab.render.network import render_network  # noqa: PLC0415
    try:
        ds = load_input(input)
        result = analyze(ds, model=model)
    except (VennDiagramError, OSError) as e:
        exit_error(str(e))
    img = render_network(result)
    target = resolve_out(out, input, "network", "svg")
    _save_or_stream(img, target, dry_run, "network")


# ---- heatmap ---------------------------------------------------------------


@app.command("heatmap")
def cmd_heatmap(
    input: Annotated[str, typer.Argument()],
    *,
    out: Annotated[Path | None, typer.Option("--out", "-o")] = None,
    model: Annotated[str, typer.Option()] = "auto",
    cluster: Annotated[
        bool, typer.Option("--cluster/--original", help="Cluster-reorder rows/cols")
    ] = False,
    linkage: Annotated[
        str, typer.Option(help="Linkage method: average/complete/single")
    ] = "average",
    show_row_dendrogram: Annotated[bool, typer.Option()] = True,
    show_col_dendrogram: Annotated[bool, typer.Option()] = True,
    dendrogram_fraction: Annotated[
        float, typer.Option(help="Dendrogram band width as fraction (0..1)")
    ] = 0.12,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Render the pairwise statistics heatmap (with optional cluster reorder)."""
    from venn_diagram_lab.render.svg import render_cluster_heatmap_svg  # noqa: PLC0415
    try:
        ds = load_input(input)
        result = analyze(ds, model=model)
    except (VennDiagramError, OSError) as e:
        exit_error(str(e))
    if cluster:
        img = render_cluster_heatmap_svg(
            result,
            linkage=linkage,
            show_row_dendrogram=show_row_dendrogram,
            show_col_dendrogram=show_col_dendrogram,
            dendrogram_fraction=dendrogram_fraction,
        )
    else:
        # Original mode: render with dendrograms suppressed.
        img = render_cluster_heatmap_svg(
            result,
            linkage=linkage,
            show_row_dendrogram=False,
            show_col_dendrogram=False,
            dendrogram_fraction=dendrogram_fraction,
        )
    target = resolve_out(out, input, "heatmap", "svg")
    _save_or_stream(img, target, dry_run, "heatmap")


# ---- share-dist ------------------------------------------------------------


@app.command("share-dist")
def cmd_share_dist(
    input: Annotated[str, typer.Argument()],
    *,
    out: Annotated[Path | None, typer.Option("--out", "-o")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Render the Item Share Distribution histogram SVG."""
    from venn_diagram_lab.render.svg import render_share_distribution_svg  # noqa: PLC0415
    try:
        ds = load_input(input)
    except (VennDiagramError, OSError) as e:
        exit_error(str(e))
    img = render_share_distribution_svg(ds)
    target = resolve_out(out, input, "share-dist", "svg")
    _save_or_stream(img, target, dry_run, "share-dist")


# ---- all -------------------------------------------------------------------


@app.command("all")
def cmd_all(
    input: Annotated[str, typer.Argument()],
    *,
    output_dir: Annotated[
        Path, typer.Option("--output-dir", help="Destination directory (required)"),
    ],
    model: Annotated[str, typer.Option()] = "auto",
) -> None:
    """Render Venn + UpSet + Network + Heatmap + ShareDist into one directory."""
    from venn_diagram_lab.render.network import render_network  # noqa: PLC0415
    from venn_diagram_lab.render.svg import (  # noqa: PLC0415
        render_cluster_heatmap_svg,
        render_share_distribution_svg,
        render_venn_svg,
    )
    from venn_diagram_lab.render.upset import render_upset  # noqa: PLC0415
    try:
        ds = load_input(input)
        result = analyze(ds, model=model)
    except (VennDiagramError, OSError) as e:
        exit_error(str(e))
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = stem_for(input)
    bundle = [
        ("venn", render_venn_svg(result)),
        ("upset", render_upset(result)),
        ("network", render_network(result)),
        (
            "heatmap",
            render_cluster_heatmap_svg(
                result,
                linkage="average",
                show_row_dendrogram=False,
                show_col_dendrogram=False,
            ),
        ),
        ("share-dist", render_share_distribution_svg(ds)),
    ]
    for name, img in bundle:
        target = output_dir / f"{stem}__{name}.svg"
        save = img.save  # type: ignore[attr-defined]
        save(target)
        typer.echo(f"Wrote {target}")
