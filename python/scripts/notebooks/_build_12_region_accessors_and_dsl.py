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
    "from IPython.display import SVG, display\n\n"
    "import venn_diagram_lab as vdl\n\n"
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


_DSL_INTRO_MD = (
    "## 2. Boolean DSL -- one operator at a time\n\n"
    "`parse_region_expression(expr, n_sets)` translates a Boolean\n"
    "expression into a sorted list of region bitmasks. The grammar uses\n"
    "the standard precedence:\n\n"
    "| Operator | Meaning | Precedence |\n"
    "|---|---|---|\n"
    "| `~` or `!` | Complement (unary) | highest |\n"
    "| `&` | Intersection | middle |\n"
    "| `+` or `|` | Union | lowest |\n"
    "| `(`, `)` | Grouping | -- |\n\n"
    "Atoms are uppercase letters `A..I`, one per set. For the 4-set\n"
    "cancer-drivers diagram, A=Vogelstein, B=COSMIC_CGC, C=OncoKB,\n"
    "D=IntOGen. Returned bitmasks are sorted and use the standard\n"
    "convention bit 0 = set A.\n"
)

_DSL_ATOM_MD = "### Atoms -- one letter per set\n"

_DSL_ATOM_CODE = (
    "print('A   ->', vdl.parse_region_expression('A', n_sets=4))\n"
    "print('D   ->', vdl.parse_region_expression('D', n_sets=4))\n"
)

_DSL_AND_MD = (
    "### Intersection (`&`) -- regions that include both sides\n"
)

_DSL_AND_CODE = (
    "print('A & B       ->', vdl.parse_region_expression('A & B', n_sets=4))\n"
    "print('A & B & C   ->', vdl.parse_region_expression('A & B & C', n_sets=4))\n"
    "print('A & B & C & D ->', vdl.parse_region_expression('A & B & C & D', n_sets=4))\n"
)

_DSL_OR_MD = (
    "### Union (`+` or `|`) -- regions that include either side\n"
)

_DSL_OR_CODE = (
    "print('A + B ->', vdl.parse_region_expression('A + B', n_sets=4))\n"
    "print('A | B ->', vdl.parse_region_expression('A | B', n_sets=4))\n"
)

_DSL_NOT_MD = (
    "### Complement (`~` or `!`) -- regions that EXCLUDE the operand\n"
)

_DSL_NOT_CODE = (
    "print('~A ->', vdl.parse_region_expression('~A', n_sets=4))\n"
    "print('!A ->', vdl.parse_region_expression('!A', n_sets=4))\n"
)

_DSL_PARENS_MD = (
    "### Parentheses + combined operators\n\n"
    "`A & (B + C)` -- items in A AND in at least one of B or C. Note that\n"
    "without parentheses, `A & B + C` would parse as `(A & B) + C` due to\n"
    "intersection's higher precedence.\n"
)

_DSL_PARENS_CODE = (
    "print('A & (B + C)     ->', vdl.parse_region_expression('A & (B + C)', n_sets=4))\n"
    "print('(A | B) & C     ->', vdl.parse_region_expression('(A | B) & C', n_sets=4))\n"
    "print('A & ~B & ~C & ~D ->', vdl.parse_region_expression('A & ~B & ~C & ~D', n_sets=4))\n"
)

_DSL_UNSAT_MD = (
    "### Unsatisfiable expressions return an empty list\n\n"
    "Some expressions admit no region. The parser does not raise; it\n"
    "returns `[]` so the result composes cleanly with downstream code.\n"
)

_DSL_UNSAT_CODE = (
    "print('A & ~A ->', vdl.parse_region_expression('A & ~A', n_sets=4))\n"
)

_SHOW_ITEMS_MD = (
    "## 3. Drawing item names inside the regions (`show_items=True`)\n\n"
    "`render_venn_svg(..., show_items=True)` replaces the per-region count\n"
    "text with the actual item identifiers as multi-line `<tspan>`\n"
    "content. Tune the layout via `item_options`:\n\n"
    "| Key | Default | Effect |\n"
    "|---|---|---|\n"
    "| `max_items_per_region` | 20 | Cap items shown; the rest collapse to `+N more` |\n"
    "| `ncol_items` | 1 | Wrap items into multiple columns |\n"
    "| `truncate_long_names` | 12 | Trim long labels (0 disables) |\n"
    "| `line_height` | 10 | tspan `dy` for each line |\n"
    "| `font_size` | 8 | text font size |\n"
    "| `show_counts_with_items` | False | If True, prepend a bold count |\n"
    "| `ellipsis` | `'...'` | Suffix on truncated labels |\n\n"
    "Below: render the cancer-drivers diagram with item names, capped at\n"
    "6 per region so the dense 4-way intersection stays readable, with\n"
    "labels truncated to 10 characters.\n"
)

_SHOW_ITEMS_CODE = (
    "img = vdl.render_venn_svg(\n"
    "    res,\n"
    "    show_items=True,\n"
    "    item_options={\n"
    "        'max_items_per_region': 6,\n"
    "        'truncate_long_names': 10,\n"
    "        'line_height': 11,\n"
    "    },\n"
    ")\n"
    "display(SVG(img.svg))\n"
)

_HIGHLIGHT_INTRO_MD = (
    "## 4. Spotlight mode (`highlight=...`)\n\n"
    "`render_venn_svg(..., highlight=...)` desaturates every set shape\n"
    "that does NOT contribute to at least one highlighted region.\n"
    "Highlighted regions keep their original fill; the rest fade to\n"
    "`#cccccc` at 25% opacity. The argument accepts EITHER a sequence of\n"
    "region labels (`'AB'`, `'ABC'`, ...) OR a sequence of region\n"
    "bitmasks (integers). The two forms are interchangeable -- use\n"
    "whichever is more convenient.\n"
)

_HIGHLIGHT_LABEL_MD = (
    "### Label form -- spell out the regions of interest\n\n"
    "Below: spotlight the AB and ABC regions of the 4-set diagram. C and\n"
    "D shapes stay coloured because they contribute to ABC; D shape fades\n"
    "because it does not contribute to either AB or ABC.\n"
)

_HIGHLIGHT_LABEL_CODE = (
    "img = vdl.render_venn_svg(res, highlight=['AB', 'ABC'])\n"
    "display(SVG(img.svg))\n"
)

_HIGHLIGHT_MASK_MD = (
    "### Bitmask form -- use the DSL output directly\n\n"
    "The Boolean DSL returns a list of integer bitmasks. Pass it straight\n"
    "into `highlight=`. Below: spotlight every region where A and B BOTH\n"
    "participate (i.e. masks AB, ABC, ABD, ABCD).\n"
)

_HIGHLIGHT_MASK_CODE = (
    "masks = vdl.parse_region_expression('A & B', n_sets=4)\n"
    "print('Highlighting masks:', masks)\n"
    "img = vdl.render_venn_svg(res, highlight=masks)\n"
    "display(SVG(img.svg))\n"
)

_COMPOSE_MD = (
    "## 5. Composability -- one chain end to end\n\n"
    "The four pieces compose: write a Boolean expression in the DSL,\n"
    "get a mask list back, pass it to `highlight=`, and optionally turn\n"
    "on `show_items=True` to also draw the gene names. The example\n"
    "below highlights the genes that EITHER all-three Vogelstein + COSMIC\n"
    "+ OncoKB share OR appear in COSMIC + OncoKB but NOT Vogelstein.\n"
)

_COMPOSE_CODE = (
    "expr = 'A & B & C + ~A & B & C'\n"
    "masks = vdl.parse_region_expression(expr, n_sets=4)\n"
    "print(f'Expression  : {expr!r}')\n"
    "print(f'Mask list   : {masks}')\n\n"
    "img = vdl.render_venn_svg(\n"
    "    res,\n"
    "    highlight=masks,\n"
    "    show_items=True,\n"
    "    item_options={'max_items_per_region': 5, 'truncate_long_names': 9},\n"
    ")\n"
    "display(SVG(img.svg))\n"
)

_CLI_INTRO_MD = (
    "## 6. The same operations from the shell (`vdl`)\n\n"
    "Every Python helper covered above is also a CLI subcommand. This\n"
    "matters when you want a one-liner in a Snakemake rule, a Make\n"
    "target, or an interactive shell. The notebook drives the CLI via\n"
    "`subprocess.run` so the output is reproducible regardless of which\n"
    "shell you usually use.\n"
)

_CLI_REGIONS_MD = (
    "### `vdl data regions` -- resolve a Boolean expression to masks\n\n"
    "Useful as a debug / validator and as a script-friendly way to get a\n"
    "comma-separated mask list onto the shell.\n"
)

_CLI_REGIONS_CODE = (
    "import subprocess\n"
    "import sys\n"
    "from pathlib import Path\n\n"
    "VDL = str(Path(sys.executable).parent / 'vdl')\n\n"
    "r = subprocess.run(\n"
    "    [VDL, 'data', 'regions', '--expr', 'A & B + B & C', '--n-sets', '4'],\n"
    "    capture_output=True, text=True, check=True,\n"
    ")\n"
    "print('masks  :', r.stdout.strip())\n\n"
    "r = subprocess.run(\n"
    "    [VDL, 'data', 'regions', '--expr', 'A & B + B & C',\n"
    "          '--n-sets', '4', '--format', 'labels'],\n"
    "    capture_output=True, text=True, check=True,\n"
    ")\n"
    "print('labels :', r.stdout.strip())\n"
)

_CLI_ITEMS_MD = (
    "### `vdl data items` -- list items by set combination\n\n"
    "Three modes -- `intersection`, `exclusive`, `union` -- mirror the\n"
    "Python accessors. Output is one item per line; use `--out -` for\n"
    "stdout or `--out path.txt` for a file.\n"
)

_CLI_ITEMS_CODE = (
    "r = subprocess.run(\n"
    "    [VDL, 'data', 'items', 'dataset_real_cancer_drivers_4',\n"
    "          '--mode', 'exclusive', '--sets', 'A,B', '--out', '-'],\n"
    "    capture_output=True, text=True, check=True,\n"
    ")\n"
    "items = r.stdout.splitlines()\n"
    "print(f'Items exclusively in A and B (not in C or D): {len(items)}')\n"
    "print('First 10:', items[:10])\n"
)

_CLI_RENDER_MD = (
    "### `vdl render venn --highlight-expr` -- spotlight render to file\n\n"
    "Combines the DSL parsing and the spotlight render into one\n"
    "command. The `--highlight-expr` flag is preferred over comma-list\n"
    "`--highlight` when the expression is more complex than two or three\n"
    "labels.\n"
)

_CLI_RENDER_CODE = (
    "import tempfile\n\n"
    "with tempfile.TemporaryDirectory() as tmp:\n"
    "    out_path = Path(tmp) / 'spotlight.svg'\n"
    "    r = subprocess.run(\n"
    "        [VDL, 'render', 'venn', 'dataset_real_cancer_drivers_4',\n"
    "              '--show-items', '--max-items-per-region', '6',\n"
    "              '--truncate-long-names', '10',\n"
    "              '--highlight-expr', 'A & B & ~C & ~D',\n"
    "              '--out', str(out_path)],\n"
    "        capture_output=True, text=True, check=True,\n"
    "    )\n"
    "    svg_text = out_path.read_text()\n"
    "    print(f'Wrote {len(svg_text)} chars to {out_path.name}')\n"
    "    display(SVG(svg_text))\n"
)

_DECISION_MD = (
    "## 7. Which pattern when?\n\n"
    "| Use this | When |\n"
    "|---|---|\n"
    "| `intersection_items(res, [...])` | You want every item shared by a group, and you don't care whether items also appear in other sets. |\n"
    "| `exclusive_items(res, [...])` | You want items ONLY in this exact combination. Equivalent to looking up one region. |\n"
    "| `union_items(res, [...])` | You want a deduplicated candidate pool across a group. |\n"
    "| `parse_region_expression(expr, n_sets)` | You want the mask vector for a non-trivial Boolean combination (with negation or unions). |\n"
    "| `render_venn_svg(..., show_items=True)` | You want item names inside the regions for a paper figure or slide. |\n"
    "| `render_venn_svg(..., highlight=[...])` | You want a spotlight on a subset of regions; other sets fade. |\n"
    "| `vdl data items ... --out -` | Shell pipeline that needs the items (e.g. piped into another tool). |\n"
    "| `vdl data regions --expr ...` | Debug / sanity-check a DSL expression without writing Python. |\n"
    "| `vdl render venn --highlight-expr ...` | One-shot CLI render with a DSL spotlight, e.g. in a Makefile. |\n"
)

_FURTHER_READING_MD = (
    "## Further reading\n\n"
    "- [`02_real_cancer_drivers.ipynb`](02_real_cancer_drivers.ipynb)"
    " -- the same dataset with the full analysis + report pipeline.\n"
    "- [`05_statistics_deep_dive.ipynb`](05_statistics_deep_dive.ipynb)"
    " -- the statistics underlying which intersections are enriched.\n"
    "- [`07_pdf_reports.ipynb`](07_pdf_reports.ipynb)"
    " -- bundle a spotlight render into a multi-page PDF report.\n"
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
    ("md", _DSL_INTRO_MD),
    ("md", _DSL_ATOM_MD),
    ("code", _DSL_ATOM_CODE),
    ("md", _DSL_AND_MD),
    ("code", _DSL_AND_CODE),
    ("md", _DSL_OR_MD),
    ("code", _DSL_OR_CODE),
    ("md", _DSL_NOT_MD),
    ("code", _DSL_NOT_CODE),
    ("md", _DSL_PARENS_MD),
    ("code", _DSL_PARENS_CODE),
    ("md", _DSL_UNSAT_MD),
    ("code", _DSL_UNSAT_CODE),
    ("md", _SHOW_ITEMS_MD),
    ("code", _SHOW_ITEMS_CODE),
    ("md", _HIGHLIGHT_INTRO_MD),
    ("md", _HIGHLIGHT_LABEL_MD),
    ("code", _HIGHLIGHT_LABEL_CODE),
    ("md", _HIGHLIGHT_MASK_MD),
    ("code", _HIGHLIGHT_MASK_CODE),
    ("md", _COMPOSE_MD),
    ("code", _COMPOSE_CODE),
    ("md", _CLI_INTRO_MD),
    ("md", _CLI_REGIONS_MD),
    ("code", _CLI_REGIONS_CODE),
    ("md", _CLI_ITEMS_MD),
    ("code", _CLI_ITEMS_CODE),
    ("md", _CLI_RENDER_MD),
    ("code", _CLI_RENDER_CODE),
    ("md", _DECISION_MD),
    ("md", _FURTHER_READING_MD),
]


if __name__ == "__main__":
    out = (
        Path(__file__).resolve().parent.parent.parent
        / "examples"
        / "12_region_accessors_and_dsl.ipynb"
    )
    build_notebook(CELLS, out)
    print(f"Wrote {out}")
