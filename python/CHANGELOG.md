# Changelog — venn-diagram-lab (Python package)

The Python package's history is co-developed with the React web tool. The
authoritative full history lives at the repo-root [`CHANGELOG.md`][root]
under the `## v1.14.0 — 2026-05-01` and later sections; this file
summarises the Python-only changes.

[root]: https://github.com/ZoliQua/Venn-Diagram-Lab/blob/main/CHANGELOG.md

## v2.0.1 — 2026-05-03 — Citation + DOI in PyPI page README

Patch release. Embeds the v2.0.0 Zenodo DOI ([10.5281/zenodo.20000599](https://doi.org/10.5281/zenodo.20000599)) into the package README so the PyPI project page renders the correct citation block + DOI badge. (The v2.0.0 wheel was built before Zenodo minted the DOI, so its METADATA shipped a placeholder line.)

No code changes. No public-API changes.

## v2.0.0 — 2026-05-03 — first PyPI release

First public PyPI release of the headless Python companion. See the root [`CHANGELOG.md`][root] v2.0.0 section for the full feature list (mypy strict clean, 3-OS CI, OIDC trusted publisher workflow, etc.).

## v0.9.0 — 2026-05-02 (Phase 8: Polish + docs)

### Cleanup
- Mypy strict clean across all 16 source files (24 carryover errors from
  Phases 2-7 fixed: typed `_SAMPLE_REGISTRY` via `_SampleMeta` TypedDict;
  dropped 11 unused `# type: ignore` comments; typed all CLI helpers
  (`_load_dataset`, `_print_summary`, `_write_outputs`, `_emit_outputs`);
  typed PDF helpers (`_build_table_axes`, `_draw_*_table`) and added safe
  cast around `cairosvg.svg2png`'s untyped return; typed
  `RegionResult.render_*` and `to_*_tsv` methods so PDF report no longer
  hits `[no-untyped-call]`).
- `_SAMPLE_REGISTRY` cross-references the fixture-generator's `SAMPLES`
  table for future maintainers.

### Docs
- Full README rewrite (`python/README.md`): Phase 0 stub → ~190-line
  pip-page README with badges, install, quickstart, full CLI reference,
  notebook-gallery index, sample-dataset table, contributing guide.
- Docstring sweep on all 25 public-API symbols in Google style. Headline
  functions (`analyze`, `load_csv` / `load_tsv` / `load_gmt` / `load_gmx`,
  `load_sample`, `list_samples`, `RegionResult`) get full Args/Returns/Example
  blocks. Remaining 17 get accurate one-line summaries + Args/Returns or
  Attributes sections.
- Per-package CHANGELOG (this file) + `python/LICENSE` so the wheel ships a
  self-contained doc bundle.

### CI
- `.github/workflows/python-test.yml` now triggers on push to
  `feature/**` (in addition to `main`), so future feature branches get
  coverage before merge. Closes the gap that let mypy errors
  accumulate silently through Phases 2-7.
- Matrix restricted to ubuntu-latest only (was 3 OS × 3 Python). macOS +
  Windows runners both hit cairosvg's `libcairo` runtime lookup failure
  even after `brew install cairo pango` / pip install. The package works
  on those platforms locally with the right system deps; CI gap is the
  hosted runner's `ctypes.util.find_library()` can't find the bundled
  dylib/dll. Phase 9 (PyPI release) will revisit — likely via `pycairo`
  Python dep or explicit `DYLD_LIBRARY_PATH` setup.

### Behavior
- No new features. No breaking changes (the `_SampleMeta` TypedDict is
  private). Public API unchanged from v0.8.0.

## Earlier (Phases 0-7)

See the root [`CHANGELOG.md`][root] for the per-phase summaries from
v0.1.0 (Phase 0 skeleton) through v0.8.0 (Phase 7 parity tests + universe
correctness fix).

## Known limitations

- **CI is Linux-only** as of v0.9.0. macOS + Windows hosted runners can't
  resolve cairosvg's libcairo at runtime even with system deps installed.
  Local development on macOS/Windows works with the right deps
  (`brew install cairo pango` / GTK3 runtime). Phase 9 (PyPI release)
  must solve or document this so end users on those platforms get
  working PDF/PNG renders.
- `dataset_mock_streaming_platforms` parity test xfailed (strict): the
  source CSV has duplicate "Dark Matter" Title rows. The webapp's
  row-based loader counts them separately; Python's set-based
  `Dataset.items` deduplicates. Reconciling requires either a Python
  data-model refactor or an upstream CSV edit; deferred past v1.0.
- Sphinx/MkDocs documentation site is deferred past v1.0; for now the
  README + docstrings + notebook gallery are the documentation surface.
- `pytest-mpl` visual-regression tests for the renderers are deferred to
  v0.2+ to avoid font-rendering false positives across OSes.
