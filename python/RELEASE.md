# Release runbook — venn-diagram-lab

Operator-facing checklist for cutting a new release. The CI workflow
(`.github/workflows/python-publish.yml`) handles the actual upload via GitHub
OIDC, but a few manual prerequisites need to be set up once.

## One-time setup (do this before v2.0.0)

### 1. Register the PyPI Trusted Publisher

PyPI's modern publishing uses GitHub OIDC tokens (no long-lived API tokens).
You need to register the GitHub workflow as a "pending publisher" before the
first push.

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name:** `venn-diagram-lab`
   - **Owner:** `ZoliQua`
   - **Repository name:** `Venn-Diagram-Lab`
   - **Workflow name:** `python-publish.yml`
   - **Environment name:** `pypi` (matches `environment.name` in the workflow)
4. Save.

Repeat for TestPyPI at https://test.pypi.org/manage/account/publishing/ with
**Environment name:** `testpypi`.

### 2. Create the GitHub environments

In the repo Settings → Environments, create two environments:
- `pypi` — used by the production publish job
- `testpypi` — used by the dry-run job

Both can be left without protection rules for now (the OIDC scoping is
enough). Optionally, add a required reviewer for the `pypi` environment so
the production push needs explicit approval.

### 3. Enable Zenodo-GitHub integration

1. Go to https://zenodo.org/account/settings/github/
2. Find `ZoliQua/Venn-Diagram-Lab` in the list
3. Toggle it **ON**

From now on, every GitHub release Zenodo sees will be archived and assigned
a fresh DOI.

## Per-release checklist

For each release (e.g. v2.0.0):

1. **Bump versions** (Phase 9 Task E1 / E2):
   - `python/src/venn_diagram_lab/version.py::__version__`
   - `package.json::version`
   - `src/version.ts::APP_VERSION`
   - `CITATION.cff::version` and `date-released`
2. **Update `python/CHANGELOG.md` and root `CHANGELOG.md`** — describe the
   release.
3. **Verify locally:**
   ```bash
   .venv/bin/pytest python/tests -q -m "not slow"
   .venv/bin/ruff check python/
   .venv/bin/mypy --config-file python/pyproject.toml python/src/venn_diagram_lab/
   .venv/bin/python -m build python/ --outdir python/dist
   .venv/bin/twine check python/dist/*
   ```
4. **Open a PR** with the version bumps. Wait for all CI cells green.
5. **Merge to main.**
6. **Tag a release-candidate first:**
   ```bash
   git checkout main && git pull
   git tag v2.0.0-rc1
   git push origin v2.0.0-rc1
   ```
   Watch the `python-publish.yml` workflow on GitHub. The job
   `publish-testpypi` should succeed.
7. **Verify TestPyPI install:**
   ```bash
   /usr/local/bin/python3.12 -m venv /tmp/vdl-test
   /tmp/vdl-test/bin/pip install --index-url https://test.pypi.org/simple/ \
       --extra-index-url https://pypi.org/simple/ venn-diagram-lab==2.0.0rc1
   /tmp/vdl-test/bin/vdl version  # prints 2.0.0rc1
   /tmp/vdl-test/bin/vdl list-samples
   rm -rf /tmp/vdl-test
   ```
8. **If the rc looks good, tag the real release:**
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```
   Watch `publish-pypi` succeed. The package is now live on
   https://pypi.org/project/venn-diagram-lab/.
9. **Create the GitHub Release:**
   ```bash
   gh release create v2.0.0 --title "v2.0.0 — first PyPI release" \
       --notes-from-tag --verify-tag
   ```
   Zenodo will pick this up within a few minutes and mint a fresh DOI.
10. **Once Zenodo emails the new DOI** (or check
    https://zenodo.org/account/settings/github/ for the DOI link):
    - Update `CITATION.cff::doi` with the new DOI string
    - Add the DOI badge to root README.md
    - Commit:
      ```bash
      git add CITATION.cff README.md
      git commit -m "docs: update Zenodo DOI for v2.0.0"
      git push origin main
      ```

## Rollback

If the PyPI release is broken:

- **Don't try to delete from PyPI** — versions are immutable. Yank instead
  via the PyPI web UI: Project page → Manage → Releases → ... → Yank.
- Tag a `v2.0.1` patch release with the fix. Yanked versions don't appear
  in `pip install venn-diagram-lab` resolution but are still downloadable
  by exact pin.
- TestPyPI versions are also immutable but cleanup is generally not
  needed (TestPyPI is best-effort).

## Common gotchas

- **OIDC token errors in the workflow:** make sure the `permissions:` block
  is `id-token: write` and the `environment:` matches the publisher
  registration on pypi.org exactly (case-sensitive).
- **Tag/version mismatch:** the workflow's `Verify version matches tag`
  step fails fast if `version.py` doesn't match the tag (modulo PEP 440
  rc-suffix normalization). Fix the version, force-push the tag is NOT
  allowed — bump to a new tag instead.
- **cairosvg failures on user machines after install:** document in the
  README that Windows users need GTK3 runtime OR `pip install pycairo`,
  macOS users need `brew install cairo pango`. Phase 9 Task A1+A2 fixes
  this in CI; user machines are user responsibility.
