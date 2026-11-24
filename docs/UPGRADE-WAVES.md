# Upgrade waves

This page is the execution order for majors. `versions.yaml` records the
baseline; `platform/backend/app/version.py` (`APP_VERSION`) is the version of
record. The signed tag and `versions.yaml` win over any page, and the frontend
`package.json` version mirrors the platform release.

Last reviewed: **2026-11-23**.

## Version of record

| Source | Value | Role |
|---|---|---|
| `platform/backend/app/version.py` | `APP_VERSION = "5.48.0"` | Runtime version of record |
| `versions.yaml` `platform.version` | `5.48.0` | Human and CI inventory |
| `versions.yaml` `release.version` | `5.48.0` | Last released line |
| `versions.yaml` `development.version` | `5.49.0` | Next planned line |
| `platform/frontend/package.json` | `5.48.0` | Frontend build metadata |
| Signed tag | `v5.48.0` | Release evidence |

Do not hand-maintain a second major line in these files. If a value disagrees,
fix it before a release and run:

```bash
python scripts/report-versions.py --platform-only
```

The 2026-11-23 cleanup corrected the backend base from Python 3.11 to the
actual 3.13 digest, removed the retired `chart.js` / `vue-chartjs` entries in
favour of `echarts 6.1.0`, aligned the release/development versions, and moved
`vue-eslint-parser` to `devDependencies`.

## Wave order

Do one wave at a time on one host. Each wave ends with a backup, a restore
rehearsal when the database changes, the full CI suite, the security scans, and
a signed supply-chain lock.

| Wave | Change | Risk | Why now | Gate |
|---|---|---|---|---|
| **0** | Move the remaining inline `ADD COLUMN` startup migrations into Alembic | Medium | Removes the code path most likely to break during Postgres and 1.1.3 jumps | Fresh install and an upgrade from the current schema both reach the same Alembic head; startup does no schema writes |
| **1** | PostgreSQL 15 -> 17 | High | Optimizer and vacuum improvements; 15 approaches its Nov 2027 EOL | `pg_upgrade` and dump/restore both pass on a production-size copy; RLS, integrity triggers, tenant roles, and the runtime/migrator role split survive |
| **2** | Python 3.13 -> 3.14 | Low | Before the 3.13 security window matters for a pinned digest | `cryptography`, `psycopg[binary]`, and `pydantic` wheels exist for the pinned base; CI and the image build pass |
| **3** | APScheduler 3.11 -> 4.x | High | A real rewrite: async scheduler and jobstore API, with custom leader election | Scheduler race, crash-cleanup, and duplicate-job tests pass under the new API; rollback restores the old leader behavior |
| **4** | Ubuntu 24.04 -> 26.04 host | Medium | Already a test candidate with its own workflow | Postgres 17 is already running; the Docker apt key flow and the 8443 origin pass the promotion gates |
| **5** | Community / Academic 1.1.3 -> 5.x | High | The supported maintenance line needs a rehearsed path | One real 1.1.3 snapshot reaches 5.35 through `upgrade-from-backup.sh`; the inline-migration removal from Wave 0 is in place |
| **6** | Frontend Node 22 -> 24 and maintenance dependencies | Low | Build-only; the runtime stays on the pinned nginx digest | CI stays green; the bundle-size gate passes; Vue stays within the current minor line |

## Wave 0: Alembic consolidation

This is the prerequisite, not a side quest. The startup `ADD COLUMN` block in
`main.py` is a second schema authority. Postgres 17 and the 1.1.3 jump both
exercise it, and a partial failure leaves a schema neither Alembic nor the
startup code describes correctly.

Acceptance:

- A fresh database reaches the Alembic head with startup schema writes disabled.
- A database at the current release reaches the same head through the normal
  upgrade command.
- A 1.1.3 snapshot reaches the same head without a manual `ADD COLUMN` step.
- `alembic current` and `alembic heads` agree in CI.

## Wave 1: PostgreSQL 17

Test both paths on a production-size copy:

1. `pg_upgrade` in place.
2. Dump/restore through `upgrade-from-backup.sh` (this is also the DR
   rehearsal).

Verify after either path:

- RLS policies and `set_config` context still apply.
- The integrity trigger still records the actor and request id.
- The runtime role cannot perform migrations; the migrator role cannot serve
  traffic.
- `ensure-db-password.sh` and the auth tables still work.
- Backup restore, export, and the 8443 workbook origin still pass.

## Wave 2: Python 3.14

The image is digest-pinned, so this is one base-image change plus CI. Check
wheel availability for `cryptography`, `psycopg[binary]`, `pydantic`, and
`python3-saml`/`xmlsec` before opening the PR. Keep the old base digest
available for rollback.

## Wave 3: APScheduler 4.x

Treat this as an application change, not a dependency bump. The current code
has a custom leader-election path and a `shutdown_scheduler` integration. Port
the jobstore and scheduler lifecycle first, then re-run the scheduler race and
crash-cleanup tests. Do not merge it with another major.

## Wave 4: Ubuntu 26.04

Run this after Postgres 17, not beside it. The Ubuntu-next workflow is the
gate. Confirm the `docker-ce` repository key flow and the 8443 workbook origin
on the candidate image, then promote one host at a time.

## Wave 5: 1.1.3 to 5.x

Rehearse with a real 1.1.3 snapshot, not a synthetic schema. The expected path
is backup -> `upgrade-from-backup.sh` -> Alembic -> smoke. Record the exact
snapshot, the command output, and the post-upgrade schema head. If Wave 0 is
not complete, stop: the inline startup migrations are the most likely failure
point in this jump.

## Wave 6: frontend and maintenance dependencies

- Node 24 is build-only. The runtime remains the pinned nginx digest.
- Keep Vue on the current minor line until the Vue 4 decision.
- `vue-eslint-parser` belongs in `devDependencies`; it does not ship.
- The bundle-size gate in `platform/frontend/scripts/check-bundle-size.mjs`
  fails a route chunk above 600 KB or an entry above 200 KB. Split with
  `defineAsyncComponent` rather than raising the limit.

## Maintenance-risk dependencies

These are the places where upstream is the risk, not the version number:

| Dependency | Risk | Position |
|---|---|---|
| `python3-saml` | XML-signature history and the `xmlsec` build dependency | Keep the SSO hardening tests as the insurance; watch for a maintained successor |
| `ldap3` | Stable but effectively dormant | Pin; budget for a fork only if an auth bypass lands |
| `slowapi` | Thin wrapper around `limits` | If it stalls, use `limits` directly; the platform does not need the extra layer |
| `bcrypt` | Base-image and wheel version differences warn on `__bcrypt__` | Keep the pinned fallback aligned with the image |
| `osixia/openldap` | Demo-profile image line is slowing | Consider `lldap` or a maintained slapd image when the SSO demo is next touched |
| `Dex` | Frequent releases | Keep the digest bump cadence regular rather than batching |

## Renovate policy

Majors already require dashboard approval. The wave labels make the dashboard
readable:

- `wave:postgres` for the Postgres image.
- `wave:python` for the Python base image and interpreter pins.
- `wave:apscheduler` for the scheduler.
- `wave:frontend` for the frontend group.

Do not let a major sit approved for a year. Either schedule the wave or record
an exception with an owner and an expiry in `versions.yaml`.
