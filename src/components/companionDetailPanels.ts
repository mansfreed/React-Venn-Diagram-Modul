// Code-level "how do I call this?" panels for the CompanionPackageDialog.
//
// Each feature cell (Overview tab) and feature group (Features tab) of the
// Python / R companion dialogs can be clicked to open a focused modal showing
// runnable snippets. Every symbol used below is a REAL public export verified
// against the package sources:
//   - Python: python/src/venn_diagram_lab/__init__.py (__all__) + class methods
//   - R:      r/NAMESPACE (export(...)) + slot accessors
// Do not introduce function names that are not actually exported.

export type CompanionKind = 'python' | 'r';

/** A category key shared by the Overview cells and the Features groups. */
export type DetailKey = 'analysis' | 'stats' | 'viz' | 'export' | 'tooling' | 'tidyverse';

export interface DetailCodeBlock {
  /** Short label shown above the snippet, e.g. "Python" or "Load & analyze". */
  label: string;
  code: string;
}

export interface DetailPanel {
  key: DetailKey;
  /** Heading shown in the modal. */
  title: string;
  /** One-paragraph orientation above the code blocks. */
  blurb: string;
  blocks: DetailCodeBlock[];
}

// ---------------------------------------------------------------------------
// Python
// ---------------------------------------------------------------------------

const PYTHON_PANELS: Record<string, DetailPanel> = {
  analysis: {
    key: 'analysis',
    title: 'Analysis',
    blurb:
      'Load CSV / TSV / GMT / GMX or a bundled sample, run analyze() to enumerate every region, then read the set sizes or pull the items out of any region.',
    blocks: [
      {
        label: 'Load & analyze',
        code: `from venn_diagram_lab import load_csv, load_sample, analyze

# A bundled sample, or your own file
ds = load_sample("dataset_real_cancer_drivers_4")
ds = load_csv("genes_binary.csv", binary=True)   # binary=False = aggregated

result = analyze(ds)                  # auto-pick a model
result = analyze(ds, model="edwards-4")

result.set_sizes
# {'Vogelstein': 138, 'COSMIC_CGC': 581, 'OncoKB': 1231, 'IntOGen': 633}
result.regions          # dict: bitmask -> RegionData`,
      },
      {
        label: 'Pull items out of regions',
        code: `from venn_diagram_lab import (
    exclusive_items, intersection_items, union_items,
    parse_region_expression,
)

exclusive_items(result, ["Vogelstein", "OncoKB"])     # only these sets
intersection_items(result, ["Vogelstein", "OncoKB"])  # in all of them
union_items(result, ["Vogelstein", "OncoKB"])         # in any of them

# Boolean DSL (atoms A..I) -> matching region bitmasks
parse_region_expression("A & ~C", n_sets=4)`,
      },
    ],
  },
  stats: {
    key: 'stats',
    title: 'Statistics',
    blurb:
      "Every analyze() result carries a lazily-computed .statistics with Jaccard / Dice / overlap / fold-enrichment matrices and a long-form hypergeometric table. The same metrics are available as stateless helper functions.",
    blocks: [
      {
        label: 'From the result',
        code: `from venn_diagram_lab import load_sample, analyze

result = analyze(load_sample("dataset_real_cancer_drivers_4"))

stats = result.statistics       # computed once, cached
stats.jaccard                   # NxN DataFrame
stats.dice
stats.overlap_coefficient
stats.fold_enrichment
stats.hypergeometric            # long-form table, one row per set pair`,
      },
      {
        label: 'Stateless metric helpers',
        code: `from venn_diagram_lab.statistics import (
    jaccard, dice, overlap_coefficient,
    hypergeometric_p_value, fold_enrichment,
)

# illustrative counts -- plug in sizes from your own analysis
jaccard(size_a=138, size_b=1231, intersection=92)
dice(138, 1231, 92)
overlap_coefficient(138, 1231, 92)

# enrichment of an overlap against a universe of N items
hypergeometric_p_value(N=20000, K=1231, n=138, k=92)
fold_enrichment(N=20000, K=1231, n=138, k=92)`,
      },
    ],
  },
  viz: {
    key: 'viz',
    title: 'Visualization',
    blurb:
      'Five render surfaces, all driven from the analyze() result: 44 templated SVG models, area-proportional 2/3-set layouts, UpSet plots, a force-directed network, and a matplotlib backend for paper-figure composition (Venn / share-distribution / cluster-heatmap variants returning an MplImage you can drop into your own subplot grid).',
    blocks: [
      {
        label: 'Venn / UpSet / Network',
        code: `result = analyze(load_sample("dataset_real_cancer_drivers_4"))

# Templated Venn -> SvgImage (str(svg) for the markup, or .save())
svg = result.render_venn(title="Cancer drivers")
svg.save("venn.svg")

# UpSet plot -> MplImage
result.render_upset(sort_by="degree", max_columns=20).save("upset.png")

# Force-directed network -> MplImage
result.render_network(edge_metric="jaccard").save("network.png", dpi=300)`,
      },
      {
        label: 'Area-proportional (2 / 3 sets)',
        code: `from pathlib import Path
from venn_diagram_lab import Dataset, analyze, generate_proportional_svg

ds = Dataset.from_dict({
    "A": ["x", "y", "z"],
    "B": ["y", "z", "w"],
})

svg_markup = generate_proportional_svg(analyze(ds))  # raw SVG string
Path("proportional.svg").write_text(svg_markup)`,
      },
      {
        label: 'Matplotlib backend (compose into subplot grids)',
        code: `import matplotlib.pyplot as plt

from venn_diagram_lab import (
    analyze, load_sample,
    render_venn_mpl,
    render_share_distribution_mpl,
    render_cluster_heatmap_mpl,
)

ds = load_sample("dataset_real_cancer_drivers_4")
result = analyze(ds)

# Compose all three into one figure
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
render_venn_mpl(result, ax=ax[0], title="Venn (mpl)")
render_share_distribution_mpl(ds, ax=ax[1])
render_cluster_heatmap_mpl(result, ax=ax[2], linkage="average")
fig.tight_layout()
fig.savefig("paper_figure.png", dpi=300)`,
      },
    ],
  },
  export: {
    key: 'export',
    title: 'Reports & Export',
    blurb:
      "Write a multi-page PDF report or the web tool's byte-equivalent TSV files straight from the result object.",
    blocks: [
      {
        label: 'Multi-page PDF report',
        code: `result = analyze(load_sample("dataset_real_cancer_drivers_4"))

result.to_pdf_report(
    "cancer_drivers_report.pdf",
    title="Cancer drivers (4 sources)",
    include_network=True,
)`,
      },
      {
        label: 'Byte-equivalent TSV exports',
        code: `# Same files the web tool's Export buttons produce
result.to_region_summary_tsv("summary.tsv")   # Region Summary
result.to_matrix_tsv("items.tsv")             # Item Matrix
result.to_statistics_tsv("stats.tsv")         # pairwise Statistics`,
      },
    ],
  },
  tooling: {
    key: 'tooling',
    title: 'Developer Tooling',
    blurb:
      'A Typer-based CLI (vdl) for one-shot runs from the shell, plus discovery helpers for the bundled models and samples.',
    blocks: [
      {
        label: 'Shell · the vdl CLI',
        code: `vdl analyze data.csv --output report.pdf
vdl render data.csv --model edwards-4 --output venn.svg
vdl data lookup TP53            # which region(s) contain an item
vdl --help`,
      },
      {
        label: 'Discover models & samples',
        code: `from venn_diagram_lab import list_models, list_samples

[m.name for m in list_models()]   # 44 ModelInfo entries
list_samples()                    # 5 bundled dataset ids`,
      },
    ],
  },
};

// ---------------------------------------------------------------------------
// R
// ---------------------------------------------------------------------------

const R_PANELS: Record<string, DetailPanel> = {
  analysis: {
    key: 'analysis',
    title: 'Analysis',
    blurb:
      'Load CSV / TSV / GMT / GMX or a bundled sample, run analyze() to enumerate every region, then read the set sizes or pull the items out of any region.',
    blocks: [
      {
        label: 'Load & analyze',
        code: `library(vennDiagramLab)

ds <- load_sample("dataset_real_cancer_drivers_4")
ds <- load_csv("genes_binary.csv", binary = TRUE)   # binary = FALSE = aggregated

result <- analyze(ds)                    # auto-pick a model
result <- analyze(ds, model = "edwards-4")

result@set_sizes
# Vogelstein COSMIC_CGC     OncoKB    IntOGen
#        138        581       1231        633`,
      },
      {
        label: 'Pull items out of regions',
        code: `exclusive_items(result, c("Vogelstein", "OncoKB"))     # only these sets
intersection_items(result, c("Vogelstein", "OncoKB"))  # in all of them
union_items(result, c("Vogelstein", "OncoKB"))         # in any of them

# Boolean DSL (atoms A..I) -> matching region bitmasks
parse_region_expression("A & ~C", n_sets = 4L)`,
      },
    ],
  },
  stats: {
    key: 'stats',
    title: 'Analysis & Statistics',
    blurb:
      'statistics() returns an S4 StatisticsResult with the Jaccard / Dice / overlap / fold-enrichment matrices and a long-form hypergeometric table. The same metrics are available as stateless helpers with JS-style float parity.',
    blocks: [
      {
        label: 'From the result',
        code: `library(vennDiagramLab)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

st <- statistics(result)        # S4 StatisticsResult
st@jaccard                      # NxN matrix
st@dice
st@overlap_coefficient
st@fold_enrichment
st@hypergeometric               # long-form table, one row per set pair`,
      },
      {
        label: 'Stateless metric helpers',
        code: `# illustrative counts -- plug in sizes from your own analysis
jaccard(size_a = 138, size_b = 1231, intersection = 92)
dice(138, 1231, 92)
overlap_coefficient(138, 1231, 92)

# enrichment of an overlap against a universe of N items
hypergeometric_p_value(N = 20000, K = 1231, n = 138, k = 92)
fold_enrichment(N = 20000, K = 1231, n = 138, k = 92)

bh_fdr(c(0.001, 0.04, 0.20))    # Benjamini-Hochberg adjusted p-values`,
      },
    ],
  },
  viz: {
    key: 'viz',
    title: 'Visualization',
    blurb:
      'Four render surfaces driven from the analyze() result: 44 templated SVG models, area-proportional 2/3-set layouts, UpSet plots (ComplexUpset), and a force-directed network (ggraph + tidygraph).',
    blocks: [
      {
        label: 'Venn / UpSet / Network',
        code: `library(vennDiagramLab)
library(ggplot2)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

# Templated Venn -> SVG character vector
writeLines(render_venn_svg(result, title = "Cancer drivers"), "venn.svg")

# UpSet plot -> ggplot
ggsave("upset.png", render_upset(result, sort_by = "degree"), width = 8, height = 5)

# Force-directed network -> ggraph / ggplot
ggsave("network.png", render_network(result, edge_metric = "jaccard"))`,
      },
      {
        label: 'Area-proportional (2 / 3 sets)',
        code: `# Build a small 2-set dataset (2-set is exact; 3-set is approximate)
ds <- methods::new("VennDataset",
  set_names = c("Alpha", "Beta"),
  items     = list(Alpha = c("g1", "g2"), Beta = c("g2", "g3")),
  item_order = c("g1", "g2", "g3"),
  universe_size = 3L, source_path = NULL, format = "csv")

res <- analyze(ds, model = "proportional")
writeLines(generate_proportional_svg(res), "proportional.svg")`,
      },
    ],
  },
  export: {
    key: 'export',
    title: 'Reports & Export',
    blurb:
      "Write a multi-page PDF report, the web tool's byte-equivalent TSV files, an Excel workbook, or a full ZIP bundle straight from the result object.",
    blocks: [
      {
        label: 'PDF report & TSV exports',
        code: `result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

to_pdf_report(result, path = "cancer_drivers_report.pdf")

# Byte-equivalent TSV (parity-tested vs. the web tool)
to_region_summary_tsv(result, "summary.tsv")
to_matrix_tsv(result,         "items.tsv")
to_statistics_tsv(result,     "stats.tsv")`,
      },
      {
        label: 'Excel workbook & ZIP bundle',
        code: `# 3-sheet enrichment workbook (Jaccard / Dice / Intersection enrichment)
to_excel_workbook(result, "enrichment.xlsx")

# Everything (SVG + plots + TSV + xlsx + README) in one archive
to_zip_report(result, "report_bundle.zip")`,
      },
    ],
  },
  tidyverse: {
    key: 'tidyverse',
    title: 'Tidyverse & Pipelines',
    blurb:
      'geom_venn() drops a Venn straight into a ggplot stack; broom’s tidy() / glance() / augment() return tibbles ready for dplyr / targets pipelines.',
    blocks: [
      {
        label: 'ggplot2 layer',
        code: `library(vennDiagramLab)
library(ggplot2)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

ggplot() +
  geom_venn(data = result) +
  theme_void() +
  ggtitle("Cancer driver overlap (4 sources)")`,
      },
      {
        label: 'broom S3 methods',
        code: `library(broom)

tidy(result)      # one row per region
glance(result)    # one-row summary (n_sets, n_items, ...)
augment(result)   # item-level membership matrix`,
      },
    ],
  },
};

export const COMPANION_DETAIL_PANELS: Record<CompanionKind, Record<string, DetailPanel>> = {
  python: PYTHON_PANELS,
  r: R_PANELS,
};

/** Look up a category panel for a kind + key, or undefined when none is defined. */
export function getDetailPanel(kind: CompanionKind, key: DetailKey): DetailPanel | undefined {
  return COMPANION_DETAIL_PANELS[kind][key];
}

// ---------------------------------------------------------------------------
// Per-card panels (Features tab). Each individual feature card opens its own
// modal with a longer explanation and a self-contained, runnable snippet that
// shows the actual function calls. Keyed by a stable card id; the `key` field
// reuses the card id. Blurbs may contain a blank line ("\n\n") to split into
// paragraphs — the modal renders each chunk as its own <p>.
// ---------------------------------------------------------------------------

function card(key: string, title: string, blurb: string, blocks: DetailCodeBlock[]): DetailPanel {
  // Card ids are not DetailKeys, but DetailPanel.key is typed as DetailKey for
  // the category panels; cast here since the modal only reads it for display.
  return { key: key as DetailKey, title, blurb, blocks };
}

const PYTHON_CARD_PANELS: Record<string, DetailPanel> = {
  'py-viz-templates': card(
    'py-viz-templates',
    '44 SVG templates',
    'Every Venn / Euler model from the web tool ships inside the wheel as a normalised SVG template — 2-set to 9-set, covering all the major construction methods (Venn, Edwards, Anderson, Grünbaum, Bannier-Bodin, Mamakani, …). analyze() auto-selects a fitting model, or you pin one by name and render_venn_svg() fills it with your counts.\n\nlist_models() returns the catalogue with the exact name strings to pass to model=, plus each model’s set_count.',
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze, list_models, render_venn_svg

# Browse the 44 bundled templates
for m in list_models():
    print(m.name, m.set_count, m.display_name)

# Pin a specific template by name (or omit model= to auto-pick)
result = analyze(load_sample("dataset_real_cancer_drivers_4"), model="edwards-4")

svg = render_venn_svg(result, title="Cancer drivers")
svg.save("venn.svg")        # SvgImage -> .svg / .png / .pdf by extension`,
      },
    ],
  ),
  'py-viz-proportional': card(
    'py-viz-proportional',
    'Area-proportional (2 / 3 sets)',
    'For 2- and 3-set comparisons the circles can be drawn so each area is proportional to the number of items it contains. The 2-set layout is solved exactly; the 3-set layout is a least-squares approximation (circles cannot hit every target area at once).\n\ngenerate_proportional_svg() takes an analyze() result and returns the raw SVG string, ready to write to disk.',
    [
      {
        label: 'Python',
        code: `from pathlib import Path
from venn_diagram_lab import Dataset, analyze, generate_proportional_svg

ds = Dataset.from_dict({
    "A": ["g1", "g2", "g3", "g4"],
    "B": ["g3", "g4", "g5"],
})

result = analyze(ds)
svg_markup = generate_proportional_svg(result, width=600)   # raw SVG string
Path("proportional.svg").write_text(svg_markup)`,
      },
    ],
  ),
  'py-viz-upset': card(
    'py-viz-upset',
    'UpSet plots',
    'Once the set count passes 4–5 a classic Venn becomes unreadable; an UpSet plot lays the intersections out as a matrix plus a bar chart instead. render_upset() returns an MplImage (a matplotlib figure wrapper) you can save as PNG / PDF / SVG.\n\nOrder columns by intersection size or by degree, cap them with max_columns, and drop small intersections with a minimum-count threshold.',
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze, render_upset

result = analyze(load_sample("dataset_real_msigdb_cancer_pathways"))

img = render_upset(
    result,
    sort_by="degree",      # or "size"
    max_columns=20,
    threshold=2,           # drop intersections smaller than 2
    color_mode="heatmap",  # "depth" | "heatmap" | "custom"
)
img.save("upset.png", dpi=300)`,
      },
    ],
  ),
  'py-viz-network': card(
    'py-viz-network',
    'Force-directed network',
    'An alternative view where each set is a node (sized by cardinality) and each pairwise overlap is a weighted edge. render_network() lays the graph out with a force-directed algorithm (NetworkX) and colours edges by significance, returning an MplImage.\n\nChoose what the edge weight encodes with edge_metric, and fix the layout with seed for reproducible figures.',
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze, render_network

result = analyze(load_sample("dataset_real_cancer_drivers_4"))

img = render_network(
    result,
    edge_metric="jaccard",       # "intersection" | "jaccard" | ...
    seed=42,                     # reproducible layout
    significance_threshold=0.05,
)
img.save("network.png", dpi=300)`,
      },
    ],
  ),
  'py-viz-matplotlib': card(
    'py-viz-matplotlib',
    'Matplotlib backend',
    "Three SVG renderers ship parallel matplotlib variants returning an MplImage(fig, legend) wrapper, for users composing figures into their own subplot grids. The SVG renderers stay byte-identical to the web tool's output; the matplotlib variants expose a matplotlib.figure.Figure you can drop into plt.subplots, restyle with plt.style.use(), or save at custom DPI.\n\nrender_venn_mpl() covers the 2 / 3 / 4-set classic models plus area-proportional 2 / 3-set (higher set counts raise IncompatibleModelError pointing at render_venn_svg). render_share_distribution_mpl() and render_cluster_heatmap_mpl() mirror the SVG share-distribution histogram and the cluster-ordered Jaccard heatmap. SvgImage also implements both _repr_svg_ and _repr_mimebundle_ Jupyter hooks for inline notebook display.\n\nThe vdl CLI exposes the same switch: vdl render venn / share-dist / heatmap all accept --backend {svg,mpl}, defaulting to svg.",
    [
      {
        label: 'Python · subplot composition',
        code: `import matplotlib.pyplot as plt

from venn_diagram_lab import (
    analyze, load_sample,
    render_venn_mpl,
    render_share_distribution_mpl,
    render_cluster_heatmap_mpl,
)

ds = load_sample("dataset_real_cancer_drivers_4")
result = analyze(ds)

fig, ax = plt.subplots(1, 3, figsize=(18, 6))

# Classic 4-set Venn drawn straight into ax[0]
render_venn_mpl(result, ax=ax[0],
                colors={"A": "#9b59b6", "B": "#3498db",
                        "C": "#e67e22", "D": "#1abc9c"},
                title="Custom palette")

# Item-share-distribution bars
render_share_distribution_mpl(ds, ax=ax[1])

# Cluster-reordered Jaccard heatmap (single-panel mode)
render_cluster_heatmap_mpl(result, ax=ax[2], linkage="average")

fig.tight_layout()
fig.savefig("paper_figure.png", dpi=300)`,
      },
      {
        label: 'Shell',
        code: `# vdl render {venn,share-dist,heatmap} --backend mpl  (default backend: svg)
vdl render venn       --sample --backend mpl --out venn.png
vdl render share-dist --sample --backend mpl --out share.png
vdl render heatmap    --sample --backend mpl --cluster --out heatmap.png`,
      },
    ],
  ),
  'py-stats-methods': card(
    'py-stats-methods',
    'Statistical methods',
    'Every analyze() result exposes a lazily-computed .statistics object holding the pairwise similarity matrices (Jaccard, Sørensen-Dice, Szymkiewicz-Simpson overlap), the fold-enrichment matrix, and a long-form hypergeometric table with Benjamini-Hochberg FDR. The numbers match the web tool exactly (JS-style float arithmetic).\n\nEach metric is also a stateless helper you can call on raw counts.',
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze
from venn_diagram_lab.statistics import (
    jaccard, dice, overlap_coefficient,
    hypergeometric_p_value, fold_enrichment,
)

result = analyze(load_sample("dataset_real_cancer_drivers_4"))
stats = result.statistics
stats.jaccard          # NxN DataFrame
stats.hypergeometric   # long-form table, one row per set pair

# stateless helpers on raw counts (illustrative values)
jaccard(size_a=138, size_b=1231, intersection=92)
hypergeometric_p_value(N=20000, K=1231, n=138, k=92)
fold_enrichment(N=20000, K=1231, n=138, k=92)`,
      },
    ],
  ),
  'py-export-pdf': card(
    'py-export-pdf',
    'Multi-page PDF report',
    "to_pdf_report() writes the same multi-page layout as the web tool's PDF exporter: a data-overview page, the Venn + UpSet figures, the statistics tables (with FDR colouring), the relationship network, and an 'About this report' methodology page.\n\nToggle the optional sections with keyword flags.",
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze

result = analyze(load_sample("dataset_real_cancer_drivers_4"))

result.to_pdf_report(
    "cancer_drivers_report.pdf",
    title="Cancer drivers (4 sources)",
    include_network=True,
    include_about=True,
    cluster_heatmap=False,
)`,
      },
    ],
  ),
  'py-export-tsv': card(
    'py-export-tsv',
    'Byte-equivalent TSV',
    "The three TSV writers reproduce the web tool's Export buttons exactly — byte-for-byte, so a notebook and the browser produce identical files (this is parity-tested on every release). The Region Summary lists every region with its counts, the Item Matrix is a membership table, and the Statistics file is the long-form pairwise table.\n\nEach takes a path and writes UTF-8 with the web tool's exact column order and number formatting.",
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze

result = analyze(load_sample("dataset_real_cancer_drivers_4"))

result.to_region_summary_tsv("region_summary.tsv")
result.to_matrix_tsv("item_matrix.tsv")
result.to_statistics_tsv("statistics.tsv")`,
      },
    ],
  ),
  'py-export-image': card(
    'py-export-image',
    'SVG & PNG output',
    'render_venn_svg() returns an SvgImage and render_upset() / render_network() return an MplImage. Both have a .save() that picks the format from the file extension: SvgImage writes vector .svg directly and rasterises .png / .pdf via cairo; MplImage writes .png / .pdf / .svg from the matplotlib figure.\n\nstr(svg_image) also hands you the raw SVG markup for post-processing.',
    [
      {
        label: 'Python',
        code: `from venn_diagram_lab import load_sample, analyze, render_venn_svg, render_upset

result = analyze(load_sample("dataset_real_cancer_drivers_4"))

svg = render_venn_svg(result)
svg.save("venn.svg")            # vector
svg.save("venn.png", dpi=300)   # rasterised via cairo
markup = str(svg)               # raw SVG string for post-processing

render_upset(result).save("upset.pdf")`,
      },
    ],
  ),
  'py-tool-cli': card(
    'py-tool-cli',
    'Typer CLI · vdl',
    'vdl is a Typer + Rich command-line front-end that mirrors the library: one-shot analyses, every render surface, the TSV / Excel / ZIP exporters, data-hygiene checks, the model catalogue, and reproducible workflow runs — without writing any Python.\n\nEvery command has --help, and related commands are grouped into sub-apps (render, export, report, data, model, workflow).',
    [
      {
        label: 'Shell',
        code: `# One-shot analysis -> full output bundle
vdl analyze data.tsv --output-dir out/

# Individual render surfaces
vdl render venn  data.tsv --model edwards-4 --out venn.svg
vdl render upset data.tsv --out upset.png

# Matplotlib backend on render commands (--backend mpl writes PNG)
vdl render venn       data.tsv --backend mpl --out venn.png
vdl render share-dist data.tsv --backend mpl --out share.png
vdl render heatmap    data.tsv --backend mpl --cluster --out heatmap.png

# Data hygiene + item lookup
vdl data validate data.tsv --strict
vdl data lookup   data.tsv KRAS      # which region(s) contain an item

# Discover models, get help on any sub-app
vdl model list
vdl render --help`,
      },
    ],
  ),
  'py-tool-notebooks': card(
    'py-tool-notebooks',
    'Tested example notebooks',
    'A set of self-contained Jupyter notebooks ships in python/examples/, each fully reproducible and CI-executed via nbconvert on every pull request — quickstart, the real cancer-driver case study, the statistics deep-dive, pipeline integration, CLI workflows, plot comparison, data validation and more.\n\nOpen them interactively, or run one headlessly exactly the way CI does.',
    [
      {
        label: 'Shell',
        code: `# Open the notebooks interactively
pip install venn-diagram-lab jupyter
jupyter notebook python/examples/01_quickstart.ipynb

# Or execute one headlessly (this is what CI runs)
jupyter nbconvert --to notebook --execute \\
    python/examples/05_statistics_deep_dive.ipynb`,
      },
    ],
  ),
  'py-tool-ci': card(
    'py-tool-ci',
    'Multi-OS CI',
    'Every release is validated on a Linux · macOS · Windows × Python 3.10 / 3.11 / 3.12 matrix, and the full test suite plus the parity tests against the web tool must be green before publish.\n\nThe same checks run locally with pytest.',
    [
      {
        label: 'Shell',
        code: `# Reproduce the CI test run locally
pip install pytest
pytest                 # full suite
pytest -k parity       # just the web-tool parity tests`,
      },
    ],
  ),
};

const R_CARD_PANELS: Record<string, DetailPanel> = {
  'r-viz-templates': card(
    'r-viz-templates',
    '44 SVG templates',
    'Every model from the web tool ships in the package as an SVG template. render_venn_svg() fills the chosen template with your counts via xml2 and returns a plain character vector (one string) you can writeLines() to disk. analyze() auto-selects a model, or pin one with model=.\n\nlist_models() returns a data frame of name / set_count / display_name.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)

# Browse the 44 bundled templates
head(list_models())          # data frame: name, set_count, display_name

ds <- load_sample("dataset_real_cancer_drivers_4")
result <- analyze(ds, model = "edwards-4")   # or omit model = to auto-pick

writeLines(render_venn_svg(result, title = "Cancer drivers"), "venn.svg")`,
      },
    ],
  ),
  'r-viz-proportional': card(
    'r-viz-proportional',
    'Area-proportional (2 / 3 sets)',
    '2- and 3-set diagrams can be drawn area-proportionally. solve_2set() / solve_3set() compute the circle geometry (2-set exact, 3-set approximate), generate_proportional_svg() emits the SVG, and circle_intersection_area() is the underlying lens-area primitive.\n\nBuild a small dataset and pin the proportional model.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)

ds <- methods::new("VennDataset",
  set_names = c("Alpha", "Beta"),
  items     = list(Alpha = c("g1", "g2", "g3"), Beta = c("g2", "g3", "g4")),
  item_order = c("g1", "g2", "g3", "g4"),
  universe_size = 4L, source_path = NULL, format = "csv")

result <- analyze(ds, model = "proportional")
writeLines(generate_proportional_svg(result), "proportional.svg")

# Low-level geometry helpers
solve_2set(a_only = 1, b_only = 1, ab = 2)
circle_intersection_area(r1 = 3, r2 = 2, d = 4)`,
      },
    ],
  ),
  'r-viz-upset': card(
    'r-viz-upset',
    'UpSet plots',
    'render_upset() builds an UpSet plot with ComplexUpset and returns a ggplot you can ggsave() or compose further. Order columns by size or degree, cap them with max_columns, drop small intersections with threshold, and pick a colour mode.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)
library(ggplot2)

result <- analyze(load_sample("dataset_real_msigdb_cancer_pathways"))

p <- render_upset(
  result,
  sort_by     = "degree",    # or "size"
  max_columns = 20L,
  threshold   = 2L,
  color_mode  = "heatmap"    # "depth" | "heatmap" | "custom"
)
ggsave("upset.png", p, width = 8, height = 5)`,
      },
    ],
  ),
  'r-viz-network': card(
    'r-viz-network',
    'Force-directed network',
    'render_network() draws the set-relationship graph with ggraph + tidygraph: nodes are sets, edges are weighted overlaps coloured by significance. It returns a ggplot. Choose what the edge weight encodes with edge_metric.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)
library(ggplot2)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

p <- render_network(result, edge_metric = "jaccard")  # intersection | jaccard | ...
ggsave("network.png", p, width = 7, height = 6)`,
      },
    ],
  ),
  'r-stats-s4': card(
    'r-stats-s4',
    'S4 result types + stateless metric helpers',
    'analyze() returns an S4 RegionResult carrying the input VennDataset, the enumerated regions (RegionData), the set sizes, and — via statistics() — a StatisticsResult with the Jaccard / Dice / overlap / fold-enrichment matrices and a long-form hypergeometric table. Numbers match the web tool (JS-style float parity).\n\nEvery metric is also a stateless helper; bh_fdr() adjusts a vector of p-values.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

st <- statistics(result)     # S4 StatisticsResult
st@jaccard                   # NxN matrix
st@hypergeometric            # long-form table, one row per set pair

# stateless helpers on raw counts (illustrative values)
jaccard(size_a = 138, size_b = 1231, intersection = 92)
fold_enrichment(N = 20000, K = 1231, n = 138, k = 92)
bh_fdr(c(0.001, 0.04, 0.20))`,
      },
    ],
  ),
  'r-export-pdf': card(
    'r-export-pdf',
    'Multi-page PDF report',
    "to_pdf_report() writes the web tool's multi-page layout via grDevices::pdf + patchwork — overview, Venn + UpSet, statistics tables, the relationship network, and a methodology page.",
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))
to_pdf_report(result, path = "cancer_drivers_report.pdf")`,
      },
    ],
  ),
  'r-export-tsv': card(
    'r-export-tsv',
    'Byte-equivalent TSV',
    "The three TSV writers reproduce the web tool's Export buttons byte-for-byte (12 parity tests against shared Python golden fixtures): Region Summary, Item Matrix, and the long-form pairwise Statistics.",
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

to_region_summary_tsv(result, "region_summary.tsv")
to_matrix_tsv(result,         "item_matrix.tsv")
to_statistics_tsv(result,     "statistics.tsv")`,
      },
    ],
  ),
  'r-export-image': card(
    'r-export-image',
    'SVG & PNG output',
    'render_venn_svg() returns the SVG as a character vector — writeLines() it for vector output, or rasterise to PNG with the rsvg package. The ggplot-returning renderers (UpSet, network) save through ggsave() in any device format.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)
library(ggplot2)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

# Vector SVG
writeLines(render_venn_svg(result), "venn.svg")

# Rasterise the SVG to PNG
rsvg::rsvg_png("venn.svg", "venn.png", width = 1200)

# ggplot renderers save via ggsave()
ggsave("upset.png", render_upset(result), width = 8, height = 5)`,
      },
    ],
  ),
  'r-tid-ggplot': card(
    'r-tid-ggplot',
    'ggplot2 layer',
    'geom_venn() drops a Venn straight into a ggplot stack — pass the analyze() result as data and compose with themes, titles and other layers like any geom.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)
library(ggplot2)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

ggplot() +
  geom_venn(data = result) +
  theme_void() +
  ggtitle("Cancer driver overlap (4 sources)")`,
      },
    ],
  ),
  'r-tid-broom': card(
    'r-tid-broom',
    'broom S3 methods',
    'tidy() / glance() / augment() are registered for RegionResult and return tibbles ready for dplyr / targets pipelines. tidy() gives one row per region, glance() a one-row summary, augment() an item-level membership table.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)
library(broom)
library(dplyr)

result <- analyze(load_sample("dataset_real_cancer_drivers_4"))

tidy(result)      # one row per region
glance(result)    # n_sets, n_regions, n_items, universe_size, model, ...
augment(result)   # one row per item with set-membership columns

tidy(result) |> arrange(desc(count))`,
      },
    ],
  ),
  'r-doc-vignettes': card(
    'r-doc-vignettes',
    '8 vignettes',
    'Eight RMarkdown vignettes ship with the package and are executed on every R CMD check — quickstart, the real cancer-driver case study, proportional diagrams, UpSet vs. Venn vs. network, the statistics deep-dive, pipeline integration, PDF reports, and custom styling.\n\nBrowse or open them from an R session.',
    [
      {
        label: 'R',
        code: `library(vennDiagramLab)

# List the bundled vignettes
browseVignettes("vennDiagramLab")

# Open a specific one
vignette("v05_statistics_deep_dive", package = "vennDiagramLab")`,
      },
    ],
  ),
  'r-doc-pkgdown': card(
    'r-doc-pkgdown',
    'pkgdown reference site',
    'A full function reference and rendered vignette gallery is published with pkgdown. You can also build the site locally from a source checkout.',
    [
      {
        label: 'R',
        code: `# Build the documentation site locally (from a source checkout)
# install.packages("pkgdown")
pkgdown::build_site()`,
      },
    ],
  ),
  'r-doc-ci': card(
    'r-doc-ci',
    'Multi-OS CI · 590+ tests',
    'The package is checked on a Linux (release / devel / oldrel) × macOS × Windows matrix with R CMD check, BiocCheck runs clean of WARNINGs, and the 590+ testthat suite (including 90+ parity tests vs. the web tool) must pass before release.\n\nReproduce the checks locally.',
    [
      {
        label: 'R',
        code: `# Run the test suite the way CI does
# install.packages(c("testthat", "devtools"))
devtools::test()

# Full R CMD check
devtools::check()`,
      },
    ],
  ),
};

export const COMPANION_CARD_PANELS: Record<CompanionKind, Record<string, DetailPanel>> = {
  python: PYTHON_CARD_PANELS,
  r: R_CARD_PANELS,
};

/** Look up a per-card panel for a kind + card id, or undefined when missing. */
export function getCardPanel(kind: CompanionKind, cardId: string): DetailPanel | undefined {
  return COMPANION_CARD_PANELS[kind][cardId];
}
