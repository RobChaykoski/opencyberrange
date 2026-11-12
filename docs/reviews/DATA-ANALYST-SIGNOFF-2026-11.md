# Data analyst review and sign-off - 2.7.x upgrade

Date: 12 November 2026
Scope: development database `labdb` on `172.16.16.44`, release `2.7.0`,
schema head `0014_performance_indexes`.
Reviewer role: Data Analyst (upgrade gate).

## Authority

This review is the data-quality gate for the 2.7.x upgrade. The analyst signs
off on schema integrity, referential integrity, row/column sanity, and metric
consistency. A conditional sign-off permits the development deployment to
continue; it does not authorise production promotion while conditions remain
open. The production gate is `docs/PROD-DEPLOYMENT-VALIDATION-MATRIX.md`.

## Checks performed

| Check | Method | Result |
|---|---|---|
| Referential integrity | Every foreign key in `public` checked for orphan child rows | PASS - 0 orphans |
| Critical nulls | `users`, `tracks`, `levels`, `labs`, `lab_sessions`, `lab_completions`, `courses`, `achievements`, `platform_settings`, `revoked_tokens` | PASS - 0 unexpected nulls |
| Uniqueness | Usernames, lower(email), lab slugs, (track, level) | PASS - 0 duplicates |
| Numeric sanity | Negative durations, counters, sort orders; future timestamps | PASS - 0 |
| Status domains | `lab_sessions.status` | PASS - stopped/expired/error only |
| Report integrity | `report_exports.sha256`, `signature`, `report_id` | PASS - 0 missing |
| Lab reconciliation | DB slugs vs repository `lab.yaml` files | PASS - 178 = 169 repo + 9 intentional `demotest-*` |
| Ledger | `data_integrity_ledger` rows and attribution | WARN - 6,928 of 7,785 unattributed |
| Schema | 47 tables, 14 Alembic revisions, triggers and indexes present | PASS |
| Image pipeline | Avatar/logo validation tests | PASS - 7/7 |

## Findings

### F1 - Ledger attribution is noisy (warning, not a blocker)

89% of ledger rows have no actor. The top tables are `labs`, `lab_completions`,
`lab_sessions`, `users`, `achievements`, and `levels`. This is consistent with
seed, discovery, migration, and scheduler writes that run without an
authenticated request context. The rows are not evidence of tampering, but the
review queue becomes hard to use.

**Recommendation:** set an explicit system actor for seed/discovery/scheduler
paths, or add a `system` actor class to the ledger. Add a monthly review of
unattributed rows and a retention window (for example 24 months) so the ledger
does not grow without bound.

### F2 - Demo data is mixed with curriculum data (accepted)

Nine `demotest-*` labs exist only in the database. They are intentional test
fixtures and are not public. Keep them out of learner-facing metrics by
filtering `visibility` and `is_active`; do not delete them while demo courses
reference them.

### F3 - Retention is not scheduled (warning)

`data_integrity_ledger`, `activity_events`, and `flag_attempts` grow without a
retention job. At current volume this is not a risk, but the ledger grows with
every write platform-wide.

**Recommendation:** add a scheduler job that archives or prunes rows older than
the retention window and records the run in the ledger itself.

### F4 - Metrics definitions

Lab counts differ by source: 169 repository labs, 178 database rows (9 demo), 49
non-public rows, 160 workbook pages. The README defines the metrics; dashboards
should use the same definitions and label non-public/demo rows explicitly.

## Sign-off

**Decision: CONDITIONAL PASS for the development upgrade.**

Conditions:

1. F1: system-actor attribution or an accepted-risk note before production.
2. F3: a scheduled retention job or an accepted-risk note before production.

Signed: Data Analyst Review (OpenCyberRange upgrade gate)
Date: 2026-11-12
Next review: before the production release candidate.
