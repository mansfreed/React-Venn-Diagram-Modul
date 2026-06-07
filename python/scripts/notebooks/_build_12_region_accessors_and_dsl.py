"""Build python/examples/12_region_accessors_and_dsl.ipynb."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _build import build_notebook  # sys.path bootstrap for sibling import

# ---------------------------------------------------------------------------
# Cell content constants
# ---------------------------------------------------------------------------

_INTRO = (
    "# 12 -- Region accessors and Boolean DSL\n\n"
    "venn-diagram-lab exposes four small helpers for selecting items and\n"
    "regions inside an analysed diagram. The accessors return Python lists\n"
    "of item identifiers; the Boolean DSL parses a short expression like\n"
    "`A & B + B & C` into a list of region bitmasks; and `render_venn_svg()`\n"
    "can draw the actual item names inside each region or spotlight a\n"
    "subset of regions on top of the diagram. The four chain naturally --\n"
    "this notebook walks through each surface on the bundled cancer\n"
    "drivers sample, then composes them end-to-end.\n\n"
    "**Audience:** researchers who already analyse with venn-diagram-lab\n"
    "and want quick access to per-region item lists or presentation-ready\n"
    "spotlight renderings.\n\n"
    "**You will learn:**\n\n"
    "1. The three accessors -- `intersection_items`, `exclusive_items`,\n"
    "   `union_items` -- and three research questions they answer.\n"
    "2. The Boolean DSL grammar (`&`, `+`/`|`, `~`/`!`, parentheses,\n"
    "   atoms `A..I`) with one example per operator class.\n"
    "3. `render_venn_svg(..., show_items=True)` to draw item identifiers\n"
    "   inside each region.\n"
    "4. `render_venn_svg(..., highlight=...)` to spotlight selected regions\n"
    "   in label form or bitmask form.\n"
    "5. A composability chain: DSL expression -> mask list -> spotlight render.\n"
    "6. The same operations from the shell via `vdl data items`,\n"
    "   `vdl data regions`, and `vdl render venn --highlight-expr`.\n"
    "7. A decision table for picking the right pattern.\n"
)

_SETUP_CODE = (
    "import venn_diagram_lab as vdl\n"
    "from IPython.display import SVG, display\n\n"
    "ds = vdl.load_sample('dataset_real_cancer_drivers_4')\n"
    "res = vdl.analyze(ds)\n\n"
    "print('Set inclusive sizes (items per source catalog):')\n"
    "for name, size in res.set_sizes.items():\n"
    "    print(f'  {name:14s} {size:5d}')\n"
)

_ACCESSORS_INTRO_MD = (
    "## 1. Three accessors -- one for each membership question\n\n"
    "Three pure functions, one for each of the most common questions about\n"
    "set membership:\n\n"
    "| Function | Question it answers |\n"
    "|---|---|\n"
    "| `intersection_items(result, sets)` | Which items appear in EVERY set in `sets`? (regardless of other memberships) |\n"
    "| `exclusive_items(result, sets)` | Which items appear in EXACTLY this combination? (and in no other set) |\n"
    "| `union_items(result, sets)` | Which items appear in ANY of these sets? (deduplicated) |\n\n"
    "All three accept either set letters (`'A'`, `'B'`, ...) or display\n"
    "names (the values of `result.dataset.set_names`); the two forms may\n"
    "be mixed. Output ordering follows `dataset.item_order` for\n"
    "deterministic, reproducible results.\n"
)

_ACCESSORS_Q1_MD = (
    "### Research question 1 -- the four-way consensus\n\n"
    "*Which cancer-driver genes are shared by Vogelstein, COSMIC_CGC, and\n"
    "OncoKB?* This uses `intersection_items` because the question allows\n"
    "membership in IntOGen too -- we just want items present in all three\n"
    "named catalogs.\n"
)

_ACCESSORS_Q1_CODE = (
    "shared_three = vdl.intersection_items(\n"
    "    res, ['Vogelstein', 'COSMIC_CGC', 'OncoKB']\n"
    ")\n"
    "print(f'Shared by all three named catalogs: {len(shared_three)} items')\n"
    "print('First 10:', shared_three[:10])\n"
)

_ACCESSORS_Q2_MD = (
    "### Research question 2 -- catalog-exclusive drivers\n\n"
    "*Which drivers does Vogelstein list that no other catalog reports?*\n"
    "This uses `exclusive_items` -- items present in Vogelstein and in NONE\n"
    "of COSMIC_CGC, OncoKB, IntOGen.\n"
)

_ACCESSORS_Q2_CODE = (
    "vogelstein_only = vdl.exclusive_items(res, ['Vogelstein'])\n"
    "print(f'Vogelstein-only drivers: {len(vogelstein_only)}')\n"
    "print(vogelstein_only)\n"
)

_ACCESSORS_Q3_MD = (
    "### Research question 3 -- the candidate pool\n\n"
    "*Across Vogelstein and OncoKB combined, how big is the candidate gene\n"
    "list?* This uses `union_items` to deduplicate across the two\n"
    "catalogs.\n"
)

_ACCESSORS_Q3_CODE = (
    "candidate_pool = vdl.union_items(res, ['Vogelstein', 'OncoKB'])\n"
    "print(f'Union of Vogelstein and OncoKB: {len(candidate_pool)} unique drivers')\n"
    "print('First 10 in item_order:', candidate_pool[:10])\n"
)


# ---------------------------------------------------------------------------
# Cell list -- extended in subsequent tasks
# ---------------------------------------------------------------------------

CELLS = [
    ("md", _INTRO),
    ("code", _SETUP_CODE),
    ("md", _ACCESSORS_INTRO_MD),
    ("md", _ACCESSORS_Q1_MD),
    ("code", _ACCESSORS_Q1_CODE),
    ("md", _ACCESSORS_Q2_MD),
    ("code", _ACCESSORS_Q2_CODE),
    ("md", _ACCESSORS_Q3_MD),
    ("code", _ACCESSORS_Q3_CODE),
]


if __name__ == "__main__":
    out = (
        Path(__file__).resolve().parent.parent.parent
        / "examples"
        / "12_region_accessors_and_dsl.ipynb"
    )
    build_notebook(CELLS, out)
    print(f"Wrote {out}")
