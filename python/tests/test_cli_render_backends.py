"""Tests for the --backend {svg,mpl} CLI flag on render commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from venn_diagram_lab.cli import app

runner = CliRunner()
SAMPLE = "dataset_real_cancer_drivers_4"


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_cli_render_venn_backend_svg_writes_svg(out_dir: Path) -> None:
    out = out_dir / "venn.svg"
    res = runner.invoke(
        app,
        ["render", "venn", SAMPLE, "--backend", "svg", "--out", str(out)],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    head = out.read_bytes()[:64]
    assert head.startswith(b"<svg") or head.startswith(b"<?xml")


def test_cli_render_venn_backend_mpl_writes_png(out_dir: Path) -> None:
    out = out_dir / "venn.png"
    res = runner.invoke(
        app,
        ["render", "venn", SAMPLE, "--backend", "mpl", "--out", str(out)],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_cli_render_share_dist_backend_mpl(out_dir: Path) -> None:
    out = out_dir / "share.png"
    res = runner.invoke(
        app,
        ["render", "share-dist", SAMPLE, "--backend", "mpl", "--out", str(out)],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_cli_render_heatmap_backend_mpl(out_dir: Path) -> None:
    out = out_dir / "heatmap.png"
    res = runner.invoke(
        app,
        [
            "render", "heatmap", SAMPLE,
            "--backend", "mpl", "--cluster", "--linkage", "average",
            "--out", str(out),
        ],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_cli_render_venn_rejects_unknown_backend(out_dir: Path) -> None:
    res = runner.invoke(
        app,
        ["render", "venn", SAMPLE, "--backend", "wat", "--out", str(out_dir / "v.svg")],
    )
    assert res.exit_code != 0
    assert "backend" in res.output.lower()
