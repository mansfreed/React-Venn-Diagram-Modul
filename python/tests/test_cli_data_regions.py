"""Tests for `vdl data regions` CLI command."""

from __future__ import annotations

from typer.testing import CliRunner

from venn_diagram_lab.cli import app

runner = CliRunner()


def test_cli_data_regions_masks_format():
    res = runner.invoke(
        app, ["data", "regions", "--expr", "A & B", "--n-sets", "3"]
    )
    assert res.exit_code == 0, res.output
    assert res.output.strip() == "3,7"


def test_cli_data_regions_labels_format():
    res = runner.invoke(
        app,
        [
            "data", "regions",
            "--expr", "A & B",
            "--n-sets", "3",
            "--format", "labels",
        ],
    )
    assert res.exit_code == 0, res.output
    assert res.output.strip() == "AB,ABC"


def test_cli_data_regions_complement():
    res = runner.invoke(
        app,
        ["data", "regions", "--expr", "~A", "--n-sets", "3"],
    )
    assert res.exit_code == 0, res.output
    assert res.output.strip() == "2,4,6"


def test_cli_data_regions_rejects_unknown_format():
    res = runner.invoke(
        app,
        [
            "data", "regions",
            "--expr", "A",
            "--n-sets", "3",
            "--format", "bogus",
        ],
    )
    assert res.exit_code != 0


def test_cli_data_regions_propagates_parser_errors():
    res = runner.invoke(
        app, ["data", "regions", "--expr", "A & B &", "--n-sets", "3"]
    )
    assert res.exit_code != 0
    assert "Malformed" in res.output or "malformed" in res.output
