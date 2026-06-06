"""Cross-package parity: Python DSL output matches R DSL output.

This test enforces that ``parse_region_expression`` in Python returns
the same sorted bitmask list as the R implementation for the same
input. The mask lists below were independently verified against R;
any divergence here means one side regressed.
"""

from __future__ import annotations

import pytest

from venn_diagram_lab import parse_region_expression


@pytest.mark.parametrize(
    ("expr", "n_sets", "expected"),
    [
        # Single atoms.
        ("A", 3, [1, 3, 5, 7]),
        ("B", 3, [2, 3, 6, 7]),
        ("C", 3, [4, 5, 6, 7]),
        # Intersection.
        ("A & B", 3, [3, 7]),
        ("A & B & C", 3, [7]),
        ("A & B", 4, [3, 7, 11, 15]),
        ("A & B & C", 4, [7, 15]),
        # Union variants.
        ("A + B", 3, [1, 2, 3, 5, 6, 7]),
        ("A | B", 3, [1, 2, 3, 5, 6, 7]),
        # Complement.
        ("~A", 3, [2, 4, 6]),
        ("!A", 3, [2, 4, 6]),
        # Mixed.
        ("A & ~B", 3, [1, 5]),
        ("A & ~B & ~C", 3, [1]),
        ("A & B & ~C & ~D", 4, [3]),
        ("A & B & C & ~D", 4, [7]),
        ("A & B & ~C & D", 4, [11]),
        # Parentheses.
        ("A & (B + C)", 3, [3, 5, 7]),
        ("(A | B) & C", 3, [5, 6, 7]),
        # Unsatisfiable.
        ("A & ~A", 3, []),
    ],
)
def test_parity_with_r_dsl(expr: str, n_sets: int, expected: list[int]) -> None:
    assert parse_region_expression(expr, n_sets=n_sets) == expected
