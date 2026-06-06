"""Tests for the Boolean region-expression parser (Phase 11 — Feature D)."""

from __future__ import annotations

import pytest

from venn_diagram_lab import parse_region_expression


def test_single_letter_atoms():
    # For n=3, set A is bit 0 -> matches regions that include bit 0:
    # masks 1 (A), 3 (AB), 5 (AC), 7 (ABC).
    assert parse_region_expression("A", n_sets=3) == [1, 3, 5, 7]
    assert parse_region_expression("B", n_sets=3) == [2, 3, 6, 7]


def test_intersection_operator():
    # A & B -> regions with bits 0 AND 1 -> masks 3 (AB), 7 (ABC).
    assert parse_region_expression("A & B", n_sets=3) == [3, 7]
    assert parse_region_expression("A & B & C", n_sets=3) == [7]


def test_union_operators():
    # A + B -> all masks with either bit 0 OR bit 1 set.
    assert parse_region_expression("A + B", n_sets=3) == [1, 2, 3, 5, 6, 7]
    assert parse_region_expression("A | B", n_sets=3) == [1, 2, 3, 5, 6, 7]


def test_complement_operators():
    # ~A -> masks where bit 0 is NOT set -> 2 (B), 4 (C), 6 (BC).
    assert parse_region_expression("~A", n_sets=3) == [2, 4, 6]
    assert parse_region_expression("!A", n_sets=3) == [2, 4, 6]


def test_parentheses_for_grouping():
    # A & (B + C) = (A & B) + (A & C)
    expected = sorted(
        set(parse_region_expression("A & B", n_sets=3))
        | set(parse_region_expression("A & C", n_sets=3))
    )
    assert parse_region_expression("A & (B + C)", n_sets=3) == expected


def test_combined_intersection_and_complement():
    # A & ~B = "in A but not in B"
    # masks with bit 0 set AND bit 1 NOT set: 1 (A) and 5 (AC).
    assert parse_region_expression("A & ~B", n_sets=3) == [1, 5]


def test_rejects_empty_expression():
    with pytest.raises(ValueError, match="empty"):
        parse_region_expression("", n_sets=3)


def test_rejects_trailing_operator():
    with pytest.raises(ValueError, match=r"[Mm]alformed"):
        parse_region_expression("A & B &", n_sets=3)


def test_rejects_unbalanced_parens():
    with pytest.raises(ValueError, match=r"[Pp]arenthes"):
        parse_region_expression("(A & B", n_sets=3)


def test_rejects_atoms_out_of_range():
    with pytest.raises(ValueError, match="out of range"):
        parse_region_expression("D", n_sets=3)


def test_unsatisfiable_returns_empty_list():
    # A & ~A in any n_sets matches no region
    assert parse_region_expression("A & ~A", n_sets=3) == []


def test_n_sets_validation():
    with pytest.raises(ValueError, match="n_sets"):
        parse_region_expression("A", n_sets=1)
    with pytest.raises(ValueError, match="n_sets"):
        parse_region_expression("A", n_sets=10)
