# Production deployment validation matrix - 2.7.x upgrade

Status: **DEPLOYED BY EXPLICIT OWNER OVERRIDE; GATE STILL NOT SATISFIED** (P4/P5 NOT RUN).
Environment: development host `172.16.16.44` (`ocrv2`) and production host
`172.16.16.41` (`rchaykoski`), release `2.7.0`, deployed 12 November 2026.

## Gate rule

Promote to production **only when every required row below is PASS** and the
release owner has signed the bottom of this file. A single FAIL or NOT RUN
blocks promotion. Optional rows do not block, but must be listed in the release
notes.

## Matrix

| ID | Gate | Required | Status | Evidence |
|---|---|---|---|---|
| B1 | Backend unit/integration tests | Yes | PASS | `pytest`: 290 passed, 182 skipped locally; CI runs the DB-backed set on PostgreSQL 17 |
| B2 | Frontend lint | Yes | PASS | 0 errors, 132 warnings |
| B3 | Frontend production build | Yes | PASS | `vite build` succeeds |
| B4 | Lab validation | Yes | PASS | `validate-lab.py --all`: 169 labs, 0 errors, 0 warnings |
| B5 | Supply-chain lock | Yes | PASS | 42 files, 169 lab hashes match |
| B6 | Licence compliance | Yes | PASS | `check-licences.py`: OK |
| B7 | SPA security headers / CSP hash | Yes | PASS | `check-nginx-security-headers.py`, `check-csp-hash.py` |
| B8 | External images in learner content | Yes | PASS | `check-external-images.py`: none |
| B9 | Documentation links and assets | Yes | PASS | 583 Markdown files, no broken links; assets PASS |
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
| D5 | Ledger attribution | No | WARN | Historical 3,927 unattributed rows remain in the 7-day window; new CLI/seed writes are system-attributed via `application_name=ocr-app-cli`. Verified: 169 lab-discovery updates recorded as `system`; historical rows age out |
| D6 | Stale lab rows | No | PASS | 178 DB labs = 169 repo + 9 intentional `demotest-*` |
| P1 | Backup restore drill | Yes | PASS | `pg_dump` + `pg_restore` into a scratch database; counts match exactly (141 users, 178 labs, 230 completions, 158 achievements) |
| P2 | Upgrade rehearsal 2.6 -> 2.7 | Yes | PASS | Scratch DB downgraded 0014 -> 0011 (2.6-era head) and upgraded back to 0014; row counts unchanged (141/178/230) |
| P3 | Rollback rehearsal | Yes | PASS | Full `pg_dump`/`pg_restore` rollback plus the Alembic downgrade path above |
| P4 | Signed release tag | Yes | NOT RUN | No release signing key is available in this environment; tag signing remains an operator step |
| P5 | Production-shaped host rehearsal | Yes | NOT RUN | No second production-shaped host; dev uses the dev compose profile |
| P6 | Email delivery | Yes | PASS | Mailpit sink on the compose network; `/api/settings/mail/test` delivered "SWOCTS Cyber Range mail test" to admin@example.com |
| P7 | WireGuard / Peer Manager | Yes | PASS | Hardened build on `172.17.0.1:5000`; `/peers` returns 401 without a key and 200 with the backend key; `preshared_key` nulled |
| P8 | RangeBox desktop launch | Yes | PASS | Spawned session 497 (`high-school-9-1-rangebox-first-steps`): running in 15s, RangeBox and portal containers up, stop initiated |
| P9 | Exhaustive button/flow E2E | No | PARTIAL | Route-level Playwright smoke passed; not every button |
| P10 | Dependency/image digest pinning | No | PARTIAL | Base images remain tag-pinned; digests reported at runtime |

## Result

!!! note "12 November 2026 dev verification"
    The Cyber DNA 2026.14 update (cap 99, per-branch decay, 40-hour continuing
    education, 30-day trend, evidence-strength point sizing) and the RangeBox
    refinements (quality presets, Ctrl+Alt+Del, native fullscreen, flag capture,
    text-only file guard, pop-out window, workbook embed) were deployed to dev
    `.44` at `ad659047` and verified. Manual screenshots were captured from the
    dev profile: `Manual-Lite/02_Student_Guide/img/profile-cyber-dna.png`,
    `profile-dna-tree.png`, `profile-dna-continuing-education.png`,
    `profile-cyber-gps.png`, and `Workbook/assets/workbook-reading.png`. The
    rendered manual page `.../22_Navigating_Your_Cyber_DNA/` and the workbook
    Home both loaded with all images. CLI and seed scripts now set
    `application_name=ocr-app-cli`, so new writes are attributed to `system`
    instead of `unattributed`; historical rows in the 7-day window remain until
    they age out. This note does not change the production gate: P4 and P5
    remain NOT RUN.

- Required PASS: 31
- Required FAIL: 0
- Required NOT RUN: 2 (P4 signed tag, P5 production-shaped host)
- Warnings: 1 (D5)
- Completion: **31 of 33 required gates (94%)**

**Decision: DO NOT PROMOTE.** The application is healthy on dev, but the
production-readiness gates for restore, upgrade/rollback rehearsal, signed
release, and the infrastructure integrations are not complete.

## Production deployment evidence (explicit override)

The release owner explicitly overrode the gate on **12 November 2026** and
deployed production `172.16.16.41` as `rchaykoski`. P4 and P5 remain **NOT RUN**;
this section records what was actually deployed, not a gate pass.

| Check | Evidence |
|---|---|
| Pre-deploy backup | `~/opencyberrange/.backups/prod-pre-deploy-20261112_190547/labdb.dump` (796 KB, `pg_restore -l` valid) |
| Pre-deploy database | Head `0008_mitre_attack`; 42 users, 164 labs, 124 completions |
| Post-deploy database | Head `0014_performance_indexes`; 42 users, 169 labs, 124 completions |
| Migrations | `0008 -> 0009 -> 0010 -> 0011 -> 0012 -> 0013 -> 0014` completed on startup |
| New lab images | Prebuilt the 5 new labs before discovery; all images present |
| Curriculum | `seed_curriculum.py` created OT level 2; `discover_labs.py` created 5 labs, 169 validated |
| Containers | `ocr-frontend`, `ocr-backend`, `ocr-db`, `ocr-valkey`, `ocr-docker-proxy` healthy |
| Health | `/health` 200; `/api/version` 2.7.0; frontend `/login` 200 |
| Wiki | Rebuilt 13 sites; `22_Navigating_Your_Cyber_DNA` and the workbook Home present with images |
| Integrity | 12 tracks, 54 levels, 169 labs, 43 chapters, 1 course; 0 chain breaks |
| Backup volume | `backups_data` chowned to `10001:10001`; **Create snapshot** produced `ocr_backup_20261112_192620.sql` (2.5 MB) |
| Software integrity | `software-integrity.json` regenerated from the current lock; **169/169 labs match**, 0 mismatched/missing/extra |
| Feature flags | `advanced_dna_insights_enabled=true`; production profile verified with Cyber GPS, Career Atlas, Momentum, Cyber DNA 2026.14, CE, and trend lines |
| Public About | Primary button text contrast verified at **5.17:1** in dark mode |

The first production snapshot attempt failed because the existing `backups_data`
volume was owned by `root` while the backend runs as UID `10001`. The volume
ownership was corrected and verified. The software-integrity mismatch came from
a stale `software-integrity.json` after the two lab READMEs were repaired for
mojibake; the manifest was regenerated and CI now checks it against the lock.

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
| Release owner override | rchaykoski | Deployed by explicit override; P4/P5 NOT RUN | 2026-11-12 |
| Data analyst | | PASS on P1-P3; D5 conditional | 2026-11-12 |
| Security reviewer | | PASS on P7; P4/P10 pending | 2026-11-12 |
