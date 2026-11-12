# Production deployment validation matrix - 2.7.x upgrade

Status: **NOT READY FOR PRODUCTION** (see the gate rule).
Environment: development host `172.16.16.44` (`ocrv2`), release `2.7.0`,
validated 12 November 2026.

## Gate rule

Promote to production **only when every required row below is PASS** and the
release owner has signed the bottom of this file. A single FAIL or NOT RUN
blocks promotion. Optional rows do not block, but must be listed in the release
notes.

## Matrix

| ID | Gate | Required | Status | Evidence |
|---|---|---|---|---|
| B1 | Backend unit/integration tests | Yes | PASS | `pytest`: 290 passed, 179 skipped locally; CI runs the DB-backed set on PostgreSQL 17 |
| B2 | Frontend lint | Yes | PASS | 0 errors, 132 warnings |
| B3 | Frontend production build | Yes | PASS | `vite build` succeeds |
| B4 | Lab validation | Yes | PASS | `validate-lab.py --all`: 169 labs, 0 errors, 0 warnings |
| B5 | Supply-chain lock | Yes | PASS | 42 files, 169 lab hashes match |
| B6 | Licence compliance | Yes | PASS | `check-licences.py`: OK |
| B7 | SPA security headers / CSP hash | Yes | PASS | `check-nginx-security-headers.py`, `check-csp-hash.py` |
| B8 | External images in learner content | Yes | PASS | `check-external-images.py`: none |
| B9 | Documentation links and assets | Yes | PASS | 577 Markdown files, no broken links; assets PASS |
| B10 | Compose config and image builds | Yes | PASS | Backend and frontend images build; compose config valid |
| B11 | Alembic head | Yes | PASS | Dev DB at `0014_performance_indexes`; startup upgrade clean |
| R1 | Health and version on dev | Yes | PASS | `/health` 200, `/api/version` 2.7.0 |
| R2 | Connection-pool burst | Yes | PASS | 36 concurrent dashboard/admin requests in 2s; 11/20 pool connections; no QueuePool errors |
| R3 | Scheduler tick responsiveness | Yes | PASS | 16/16 health samples at 200 through the 120s tick |
| R4 | Software integrity endpoint | Yes | PASS | 169/169 labs match; 0 mismatched/missing/extra; 0.2s |
| R5 | CyberChef panel | Yes | PASS | `/tools/cyberchef/` 200, assets 200, inline-script hashes match CSP |
| R6 | High-contrast theme | Yes | PASS | Theme cycle dark/light/contrast; contrast tokens present in the built bundle |
| R7 | Mobile shell (student) | Yes | PASS | 390x844: dashboard, exercises, profile, rangebox; 0 overflow, 0 console errors, tab bar present |
| R8 | Mobile shell (admin/instructor) | Yes | PASS | 390x844: dashboard, admin, instructor; notices present; 0 overflow/errors |
| R9 | New OT lab (S7comm) | Yes | PASS | Seeded id 187, image prebuilt, DB1 read returns the flag |
| R10 | Image upload hardening | Yes | PASS | 7 tests: PNG accepted/re-encoded; SVG, HTML, mismatch, oversized rejected |
| D1 | FK orphan scan (all FKs) | Yes | PASS | No orphan rows reported |
| D2 | Nulls in critical columns | Yes | PASS | users/labs/levels/sessions/completions/settings: 0 |
| D3 | Duplicate usernames/emails/slugs | Yes | PASS | 0 |
| D4 | Numeric sanity | Yes | PASS | No negative durations/counters, no future timestamps |
| D5 | Ledger attribution | No | WARN | 6,928 of 7,785 rows unattributed (seed/CLI/system writes); review queue noisy |
| D6 | Stale lab rows | No | PASS | 178 DB labs = 169 repo + 9 intentional `demotest-*` |
| P1 | Backup restore drill | Yes | PASS | `pg_dump` + `pg_restore` into a scratch database; counts match exactly (141 users, 178 labs, 230 completions, 158 achievements) |
| P2 | Upgrade rehearsal 2.6 -> 2.7 | Yes | NOT RUN | Dev was already on 2.7.x |
| P3 | Rollback rehearsal | Yes | NOT RUN | No documented rollback test this cycle |
| P4 | Signed release tag | Yes | NOT RUN | `v2.7.0` remains the documented unsigned exception; new tag not cut |
| P5 | Production-shaped host rehearsal | Yes | NOT RUN | No staging host identical to production |
| P6 | Email delivery | Yes | NOT RUN | No SMTP transaction tested |
| P7 | WireGuard / Peer Manager | Yes | PASS | Hardened build on `172.17.0.1:5000`; `/peers` returns 401 without a key and 200 with the backend key; `preshared_key` nulled |
| P8 | RangeBox desktop launch | Yes | NOT RUN | No interactive desktop session this cycle |
| P9 | Exhaustive button/flow E2E | No | PARTIAL | Route-level Playwright smoke passed; not every button |
| P10 | Dependency/image digest pinning | No | PARTIAL | Base images remain tag-pinned; digests reported at runtime |

## Result

- Required PASS: 27
- Required FAIL: 0
- Required NOT RUN: 6 (P2-P6, P8)
- Warnings: 1 (D5)
- Completion: **27 of 33 required gates (82%)**

**Decision: DO NOT PROMOTE.** The application is healthy on dev, but the
production-readiness gates for restore, upgrade/rollback rehearsal, signed
release, and the infrastructure integrations are not complete.

## Exit criteria for the next attempt

1. Run P1-P8 on a production-shaped host and record evidence in this file.
2. Cut and sign the release tag; update `docs/RELEASES.md`.
3. Either fix D5 (set actor context for seed/discovery/scheduler writes) or
   record an accepted-risk note with a retention policy for the ledger.
4. Re-run B1-B10 and R1-R10 on the release commit.
5. Only then change this file to `READY FOR PRODUCTION` and sign below.

## Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Release owner | | | |
| Data analyst | | Conditional (see D5) | 2026-11-12 |
| Security reviewer | | PASS on P7; P4/P10 pending | 2026-11-12 |
