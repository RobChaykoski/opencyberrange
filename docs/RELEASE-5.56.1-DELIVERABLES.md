# Release 5.56.1 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.56.1` |
| Signed tag | `v5.56.1` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `218` |
| Workbook-mapped labs | `207` |
| Public exercises | `171` |
| Supersedes | `5.56.0` |

## Fixed

| Area | Detail |
|---|---|
| Competency review queue | Regenerated `docs/COMPETENCY-REVIEW-QUEUE.md` for the 218-lab catalogue; 193 contracts await review. |
| Lab outcomes | Regenerated `platform/backend/app/data/lab-outcomes.yaml` from the current contracts. |
| NICE mappings | Regenerated the provisional NICE v2.2.0 mappings for all 218 labs, including the new researcher self-audit lab. |
| NICE reference | `docs/NICE-MAPPING.md` records the v2.2.0 snapshot, the 26 November 2026 review date, and the NIST CPRT catalogue link. The OSINT row now lists six labs. |
| Count assertions | Competency coverage, metadata-contract, lab-outcome, and competency-review tests now assert 218 labs and 193 pending reviews. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `671 passed`, `562 skipped` |
| Frontend tests | `77 passed` |
| Lab metadata schema | `218` lab.yaml files validated |
| Competency contracts | `218` contracts; validator passes |
| Lab outcomes | Generator `--check` passes |
| Competency review queue | Generator `--check` passes |
| NICE mappings | `218` mappings; generator `--check` passes |
| Workbook coverage | `207` workbook-mapped labs; `--check` passes |
| Publication audit | `0 findings` |
| Link check | `1,242` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` tracked files and `218` lab hashes match release `5.56.1` |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.56.1` | Deployed and verified |
| Production | `5.56.1` | Deployed and verified |

The release refreshes generated assessment metadata and tests. It has no
database migration and does not change the lab target.
