## Resubmission

This is a resubmission of v2.0.4, addressing the two issues raised by Uwe
Ligges on the v2.0.3 win-builder pretest:

1. **DESCRIPTION single-quoting** (reviewer ask + auto-check NOTE on Windows
   + Debian: "Possibly misspelled words"). The Description field now
   single-quotes software / package / format names: `'Venn Diagram Lab'`,
   `'UpSet'`, `'CSV'`, `'TSV'`, `'GMT'`, `'GMX'`, `'Jaccard'`, `'ggplot2'`,
   `'tidygraph'`, `'broom'`.

2. **Overall checktime 18 min > 10 min on Windows** (`re-building of vignette
   outputs ... [12m] OK`). Heavy rendering chunks in vignettes
   `v02_real_cancer_drivers`, `v04_upset_vs_venn_vs_network`,
   `v07_pdf_reports`, and `v08_custom_styling_and_export`
   (`render_upset`, `render_network`, `to_pdf_report`, `geom_venn`
   composite, `rsvg_png`/`rsvg_pdf` export) now gate on
   `NOT_CRAN <- identical(tolower(Sys.getenv("NOT_CRAN")), "true")`. On
   CRAN, only the lightweight analysis chunks evaluate, dropping vignette
   build well under one minute. The full chunks still build their figures
   under `devtools::check()` and on the 5-cell GitHub Actions CI matrix.

History:
* v2.0.1: pretest rejected on Windows due to a CRLF byte-parity bug.
* v2.0.2: the CRLF fix landed; rejected by 41-min overall checktime
  (slow tests).
* v2.0.3: `skip_on_cran()` in slow tests; rejected by 18-min overall
  checktime (slow vignettes) and DESCRIPTION-quoting NOTE.
* v2.0.4 (this submission): vignette `NOT_CRAN` gating + DESCRIPTION
  single-quoting.

No public-API changes.

## Test environments

* local macOS 14.6 (Apple Silicon), R 4.6.0
* GitHub Actions:
  * ubuntu-latest, R 4.4 (release)
  * ubuntu-latest, R 4.5 (devel)
  * ubuntu-latest, R 4.3 (oldrel-1)
  * macos-latest, R 4.6 (release)
  * windows-latest, R 4.4 (release)

## R CMD check results

0 ERRORs | 0 WARNINGs | 1 NOTE

* "New submission" — expected.

## Downstream dependencies

None — this is a new package.

## Companion packages

`vennDiagramLab` is the R companion to the
[`venn-diagram-lab` Python package](https://pypi.org/project/venn-diagram-lab/)
(v2.0.3 on PyPI) and the [Venn Diagram Lab web
tool](https://www.venndiagramlab.org/). The three implementations share the
same SVG model library and produce byte-equivalent TSV outputs (verified by
12 parity tests against shared golden fixtures).

## Notes for the reviewer

* Five bundled sample datasets in `inst/extdata/samples/` (~250 KB total)
  cover both biological (cancer drivers, MSigDB pathways) and mock
  (streaming platforms, gene sets) scenarios — all used in the eight
  vignettes for fully self-contained execution.
* `inst/extdata/models/` contains 44 SVG model templates + 44 JSON region
  files (~700 KB total) from a dozen published Venn / Edwards / Grünbaum /
  Anderson / Carroll / Mamakani / SUMO construction methods — bundled for
  byte-equivalent rendering parity with the web tool.
