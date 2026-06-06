"""Boolean region-expression parser.

Translates an expression like ``"A & B + !C"`` into a sorted list of
region bitmasks (each ``1..2^n_sets - 1``). Designed to compose with
:func:`venn_diagram_lab.render.svg.render_venn_svg` (``highlight=``
argument) and with the region-accessor family in user code.

Grammar (precedence: ``~`` / ``!`` > ``&`` > ``|`` / ``+``;
left-associative for binary operators):

* atom: ``A``, ``B``, ..., ``I`` (uppercase ASCII)
* unary: ``~`` or ``!`` (complement, against ``1..2^n_sets - 1``)
* binary: ``&`` (intersection), ``|`` or ``+`` (union)
* grouping: ``(``, ``)``

Implementation: hand-rolled tokenizer + shunting-yard to RPN + RPN
evaluation over the bitmask space ``{1..2^n_sets - 1}``.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["parse_region_expression"]

_LETTERS = "ABCDEFGHI"

# Bounds on `n_sets` accepted by the parser. Matches the 2..9 set diagram
# catalogue supported by the rest of the package.
_MIN_N_SETS = 2
_MAX_N_SETS = 9
_BINARY_ARITY = 2

# Operator precedence. Higher = binds tighter. Unary `~`/`!` is highest.
_PRECEDENCE = {"~": 4, "!": 4, "&": 3, "|": 2, "+": 2}


@dataclass(frozen=True)
class _Token:
    type: str  # "letter" | "op" | "paren"
    value: str


def _tokenize(expr: str) -> list[_Token]:
    if not expr.strip():
        raise ValueError("region expression is empty")
    tokens: list[_Token] = []
    for ch in expr:
        if ch in (" ", "\t", "\n"):
            continue
        if ch in ("&", "|", "+", "~", "!"):
            tokens.append(_Token("op", ch))
        elif ch in ("(", ")"):
            tokens.append(_Token("paren", ch))
        elif ch in _LETTERS:
            tokens.append(_Token("letter", ch))
        else:
            raise ValueError(f"Unrecognised character in region expression: {ch!r}")
    return tokens


def _is_unary(op: str) -> bool:
    return op in ("~", "!")


def _handle_op_token(
    t: _Token,
    output: list[_Token],
    op_stack: list[_Token],
    expect_operand: bool,
) -> bool:
    """Process an operator token; return the new ``expect_operand`` flag."""
    if _is_unary(t.value):
        if not expect_operand:
            raise ValueError("Malformed region expression: unexpected unary op")
        op_stack.append(t)
        return True  # still expecting operand
    if expect_operand:
        raise ValueError(
            "Malformed region expression: binary op without left operand"
        )
    while (
        op_stack
        and op_stack[-1].type == "op"
        and _PRECEDENCE[op_stack[-1].value] >= _PRECEDENCE[t.value]
    ):
        output.append(op_stack.pop())
    op_stack.append(t)
    return True


def _handle_close_paren(output: list[_Token], op_stack: list[_Token]) -> None:
    """Drain the operator stack down to the matching ``(``."""
    while op_stack:
        top = op_stack.pop()
        if top.type == "paren" and top.value == "(":
            return
        output.append(top)
    raise ValueError("Parenthesis mismatch in region expression")


def _shunting_yard(tokens: list[_Token]) -> list[_Token]:
    """Convert infix tokens to RPN via Dijkstra's algorithm."""
    output: list[_Token] = []
    op_stack: list[_Token] = []
    expect_operand = True
    for t in tokens:
        if t.type == "letter":
            if not expect_operand:
                raise ValueError("Malformed region expression: unexpected letter")
            output.append(t)
            expect_operand = False
        elif t.type == "op":
            expect_operand = _handle_op_token(t, output, op_stack, expect_operand)
        elif t.value == "(":
            op_stack.append(t)
            expect_operand = True
        else:  # t.value == ")"
            _handle_close_paren(output, op_stack)
            expect_operand = False
    while op_stack:
        top = op_stack.pop()
        if top.type == "paren":
            raise ValueError("Parenthesis mismatch in region expression")
        output.append(top)
    if expect_operand and output:
        raise ValueError("Malformed region expression: trailing operator")
    return output


def _eval_rpn(rpn: list[_Token], n_sets: int) -> list[int]:
    """Evaluate the RPN token list over the bitmask universe ``1..2^n_sets - 1``."""
    universe = set(range(1, 1 << n_sets))
    stack: list[set[int]] = []
    for t in rpn:
        if t.type == "letter":
            bit_pos = _LETTERS.index(t.value)
            if bit_pos >= n_sets:
                raise ValueError(
                    f"Letter {t.value!r} is out of range for n_sets = {n_sets}"
                )
            bit = 1 << bit_pos
            stack.append({m for m in universe if m & bit})
        elif t.type == "op":
            op = t.value
            if _is_unary(op):
                if not stack:
                    raise ValueError(
                        "Malformed expression: unary op with empty stack"
                    )
                a = stack.pop()
                stack.append(universe - a)
            else:
                if len(stack) < _BINARY_ARITY:
                    raise ValueError(
                        "Malformed expression: binary op with insufficient operands"
                    )
                b = stack.pop()
                a = stack.pop()
                if op == "&":
                    stack.append(a & b)
                elif op in ("|", "+"):
                    stack.append(a | b)
                else:
                    raise ValueError(f"Unknown operator {op!r}")
    if len(stack) != 1:
        raise ValueError("Malformed region expression: stack imbalance")
    return sorted(stack[0])


def parse_region_expression(expr: str, n_sets: int) -> list[int]:
    """Parse a Boolean region expression into a sorted list of bitmasks.

    Parameters
    ----------
    expr : str
        Boolean expression. Grammar: ``A..I`` atoms, ``&`` intersection,
        ``|`` or ``+`` union, ``~`` or ``!`` complement, parentheses for
        grouping. Precedence: unary > ``&`` > union (left-associative).
    n_sets : int
        Number of sets in the diagram (2..9). Sets the universe of valid
        bitmasks to ``1..2^n_sets - 1``.

    Returns
    -------
    list[int]
        Sorted list of region bitmasks that satisfy the expression.
        Empty list when no region satisfies (e.g. ``"A & ~A"``).

    Raises
    ------
    ValueError
        On empty expression, unbalanced parentheses, trailing operator,
        unknown character, or an atom outside the ``A..letter[n_sets-1]``
        range.
    """
    if not isinstance(expr, str):
        raise ValueError("`expr` must be a string.")
    if not isinstance(n_sets, int) or n_sets < _MIN_N_SETS or n_sets > _MAX_N_SETS:
        raise ValueError("`n_sets` must be an integer in 2..9.")
    tokens = _tokenize(expr)
    rpn = _shunting_yard(tokens)
    return _eval_rpn(rpn, n_sets)
