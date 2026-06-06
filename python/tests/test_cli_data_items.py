"""Tests for `vdl data items` CLI command."""

from __future__ import annotations

from typer.testing import CliRunner

from venn_diagram_lab.cli import app

runner = CliRunner()
SAMPLE = "dataset_real_cancer_drivers_4"


def test_cli_data_items_exclusive_mode_to_stdout():
    res = runner.invoke(
        app,
        [
            "data", "items",
            SAMPLE, "--mode", "exclusive",
            "--sets", "A,B,C", "--out", "-",
        ],
    )
    assert res.exit_code == 0, res.output
    items = [line for line in res.output.splitlines() if line]
    assert len(items) > 0


def test_cli_data_items_intersection_mode():
    res = runner.invoke(
        app,
        [
            "data", "items",
            SAMPLE, "--mode", "intersection",
            "--sets", "A,B", "--out", "-",
        ],
    )
    assert res.exit_code == 0, res.output


def test_cli_data_items_union_mode():
    res = runner.invoke(
        app,
        [
            "data", "items",
            SAMPLE, "--mode", "union",
            "--sets", "A,B", "--out", "-",
        ],
    )
    assert res.exit_code == 0, res.output


def test_cli_data_items_rejects_unknown_mode():
    res = runner.invoke(
        app,
        [
            "data", "items",
            SAMPLE, "--mode", "bogus",
            "--sets", "A,B", "--out", "-",
        ],
    )
    assert res.exit_code != 0
    assert "Unknown" in res.output


def test_cli_data_items_rejects_unknown_set():
    res = runner.invoke(
        app,
        [
            "data", "items",
            SAMPLE, "--mode", "exclusive",
            "--sets", "A,Z", "--out", "-",
        ],
    )
    assert res.exit_code != 0
    assert "Unknown set" in res.output


def test_cli_data_items_requires_sets():
    res = runner.invoke(
        app,
        [
            "data", "items",
            SAMPLE, "--mode", "exclusive", "--out", "-",
        ],
    )
    assert res.exit_code != 0
    assert "--sets" in res.output
