# Release 5.54.2 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.54.2` |
| Signed tag | `v5.54.2` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.54.1` |

## Fixed

| Area | Detail |
|---|---|
| Split-layout wiki build | `scripts/deploy-updates.sh` imported a removed `build_all_wikis` helper and required a root `mkdocs.yml`, so the development wiki volume was never rebuilt. It now runs the same one-shot `wiki-builder` service as production. |
| Legacy compose support | The updater adds `wiki-builder` to the development compose for fresh installs and writes a local `docker-compose.wiki-builder.yml` override for legacy root compose files. The override uses the existing `wiki_data` volume and the repository's `platform/wiki-builder` build context. |
| Builder inputs | The builder reads `Workbook/`, `Manual-Lite/`, `tools/wiki-gen/`, `mkdocs*.yml`, and `wikis.yaml` from the checkout. No root `mkdocs.yml` is required. |

## Verification

| Check | Result |
|---|---|
| Shell syntax | `bash -n scripts/deploy-updates.sh` passes |
| Compose config | Development and production compose files parse with the required local variables set |
| Dev wiki build | The one-shot builder ran on development and published **14** sites into the `wiki_data` volume |
| Frontend tests | `70 passed` (24 files) |
| Backend tests | `668 passed`, `559 skipped` (no backend source change) |
| Frontend lint and build | `0 errors`; build and bundle budget pass |
| Publication audit | `0 findings` |
| Link check | No broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match release `5.54.2` |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.54.2` | Deployed and verified; wiki volume rebuilt with 14 sites |
| Production | `5.54.2` | Deployed and verified |

The change is limited to the deployment tooling and the development compose.
Alembic stays at `0067_course_content_rls`, and the lab and workbook definitions
are unchanged.
