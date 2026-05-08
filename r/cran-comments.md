## Resubmission

This is a resubmission of v2.0.3, which addresses CRAN auto-check feedback
from the v2.0.2 incoming pretest:

1. **Overall checktime 41 min > 10 min on Windows** (the auto-rejection trigger):
   slow integration tests in `test-render-pdf.R`, `test-render-svg.R`,
   `test-render-upset.R`, `test-render-network.R`, and
   `test-parity-with-webapp.R` now call `testthat::skip_on_cran()` at the
   top of every `test_that()` block. The full 590+ test suite continues to
   run on the package's GitHub Actions CI matrix (5 cells: Linux release/
   devel/oldrel + macOS + Windows release), where `NOT_CRAN=true` is unset.
   On CRAN, only fast unit tests (~50 cases) execute, bringing checktime
   well under 10 minutes.

2. **Possibly misspelled words in DESCRIPTION** (NOTE on Windows + Debian):
   GMX, Jaccard, TSV, UpSet, ggplot, tidygraph — all are technical terms,
   package names, or acronyms documented in the package's `inst/WORDLIST`.

History:
* v2.0.1: pretest rejected on Windows due to a CRLF byte-parity bug in
  `cat(..., file = path)` text-mode write.
* v2.0.2: the CRLF fix landed; rejected by 41-min overall checktime.
* v2.0.3 (this submission): adds `skip_on_cran()` to slow tests.

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
