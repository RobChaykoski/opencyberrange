# MkDocs governance

Every `mkdocs-*.yml` in the repository is active. None is an orphan.

## Manual

| Config | Source | Built by |
|---|---|---|
| `mkdocs-manual-lite.yml` | `Manual-Lite/` | `.github/workflows/docs-publish.yml`; local strict build |

```bash
python -m mkdocs build -f mkdocs-manual-lite.yml --strict
python scripts/check-links.py Manual-Lite --mkdocs
python scripts/check-doc-assets.py
```

A warning fails the manual build. Keep the navigation and every page in sync.

## Workbook and track wikis

All of these use `docs_dir: Workbook` and are built from `Workbook/`,
`wikis.yaml`, and the per-track navigation:

- `mkdocs-ai.yml`
- `mkdocs-forensics.yml`
- `mkdocs-highschool.yml`
- `mkdocs-identity.yml`
- `mkdocs-linpt.yml`
- `mkdocs-malware.yml`
- `mkdocs-msfpt.yml`
- `mkdocs-netfor.yml`
- `mkdocs-osint.yml`
- `mkdocs-ot.yml`
- `mkdocs-swsec.yml`
- `mkdocs-webpt.yml`
- `mkdocs-winpt.yml`

They are exercised by:

```bash
python scripts/check-links.py Manual-Lite docs Workbook --mkdocs
python scripts/check-minor-safe.py          # high school exclusions
bash scripts/build-wiki.sh                  # builder container
bash platform/scripts/deploy-wiki.sh build  # namespaced frontend tree
bash scripts/deploy-updates.sh              # copies all configs and builds
```

`mkdocs-highschool.yml` additionally must keep its `exclude_docs` policy for
minor-safe content; `scripts/check-minor-safe.py` enforces it.

## Rules

- Do not delete a config without removing its `wikis.yaml` entry, its `Workbook`
  navigation, and every reference. A config is not orphaned merely because no
  workflow names it: the builder globs `mkdocs-*.yml`.
- Do not add a new `docs_dir` config without a matching build path and a link
  check.
- Keep the manual and workbook origins separate: the manual is published by the
  docs workflow; the workbook is served from the wiki origin.
- Run the link check before merging any navigation change.
