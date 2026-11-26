# Release 5.56.0 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.56.0` |
| Signed tag | `v5.56.0` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `218` |
| Workbook-mapped labs | `207` |
| Public exercises | `171` |
| Supersedes | `5.55.2` |

## Added

| Area | Detail |
|---|---|
| Researcher self-audit lab | `osint-1-4-researcher-self-audit` serves a safe, offline mirror of a fictional researcher's public profile, search results, synthetic breach record, photo metadata, and stale forum trail. |
| Remediation practice | The workbook asks for a finding, evidence, action, owner, and verification date, then has the learner recover the flag from the review ticket source. |
| Workbook integration | OSINT Foundations now has six exercises; the chapter review includes the self-audit and links the University of Toronto OSINT self-audit guide as additional reading. |
| Generated records | The tester manifest and competency contract are generated from the lab contract: six validation steps, one flag, and the OSINT01 competency weights. |
| Content counts | 218 lab definitions, 218 tester manifests and contracts, 207 workbook-mapped labs, and 171 public exercises. |

## Verification

| Check | Result |
|---|---|
| Lab validator | `20/21` checks passed; the one `INFO` is the optional Compose `deploy.resources` hint |
| Lab metadata schema | `218` lab.yaml files validated |
| App smoke test | Home `200`; search, profile, breach, robots, and review-ticket flag all return the expected content |
| MkDocs build | OSINT wiki builds and the new page renders |
| Competency contracts | `218` contracts; validator passes |
| Workbook coverage | `207` workbook-mapped labs |
| Publication audit | `0 findings`; `218` lab flags indexed |
| Link check | `1,241` Markdown files, no broken links |
| External targets | Pass; the lab is offline and adds no live target |
| Minor-safe check | Pass; the lab is adult OSINT and does not affect High School scope |
| Lab freshness | `218` labs, `0` stale or missing review |
| Backend tests | `671 passed`, `562 skipped` |
| Frontend tests | `77 passed` |
| Supply-chain lock | Signed; `142` tracked files and `218` lab hashes match release `5.56.0` |

## Safety notes

| Check | Result |
|---|---|
| People and records | Every person, organisation, address, credential, and breach record is fictional and labelled in the target. |
| External access | The app is dependency-free, offline, read-only, unprivileged, and has every capability dropped. |
| Data collection | The target stores no learner input and sends no telemetry. |
| Scope | The workbook tells learners not to apply the workflow to a real person and not to upload lab images to third-party services. |
| Certificate impact | The new lab is a Level 1 bonus and does not count toward the existing Level 1 certificate. |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.56.0` | Deployed and verified |
| Production | `5.56.0` | Deployed and verified |

Alembic stays at `0067_course_content_rls`. Lab discovery registers the new
exercise on both hosts.
