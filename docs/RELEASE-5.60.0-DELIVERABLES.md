# Release 5.60.0 deliverables

Release date: **2026-11-28**  
Tag: `v5.60.0`  
Base: `v5.59.0`

## Delivered

| Item | Evidence |
|---|---|
| Host updater trust fixes | `deploy-updates.sh`: signer fingerprint read from the GPG `using key` line, checkout bound to the verified tag object, prerelease tags excluded, live-session guard with `--force`, disk preflight, ERR trap, compose config check, backup retention |
| Egress containment | `harden-lab-egress.sh`: fails when a Docker network has IPv6 enabled, digest-pin warning with `HARDEN_STRICT`, `--dry-run` rule preview |
| Installer hardening | Compose pinned to v5.8.1 with per-arch SHA-256; valid Fernet fallback; no `labpass` defaults; quick start verifies the signed tag and lock before `sudo` |
| Secret hygiene check | `setup-range-server.sh --check-secrets` fails on placeholders, empty keys, a non-Fernet key, and loose modes |
| Tester flag disclosure (RB-03) | Flags redacted in every event and before section tracking; migration `0069_redact_tester_flags` scrubs stored results; `user_id` overrides are platform-admin only and tenant-checked |
| Tester timeout injection (RB-04) | Step and body timeouts coerced to 1–600 at the call and shell boundaries |
| Analytics minor exclusion (RB-05) | `_pulse_rows`/`_reaction_rows` take the minor-filtered `user_ids` set; course overview and exercises pass it |
| Privacy audit gate | `scripts/audit-privacy-exclusions.py` and `docs/PRIVACY-AUDIT.md`; Quality regenerates the report and fails on drift |
| Event-loop blocking (RB-01) | 48 async-without-await admin handlers are sync (threadpool); RangeBox bridge offloaded |
| JWT decode per request (RB-02) | Verified by `tests/test_middleware_efficiency.py`; no production change |
| Wiki header inheritance | HSTS, Referrer-Policy, and Permissions-Policy now present in generated wiki and sitemap locations |
| Tracked exceptions | `docs/TRACKED-EXCEPTIONS.md` records open findings, accepted risks, and the operations backlog |

## Verification

- Backend pytest: 695 passed, 585 skipped locally (DB-backed tests run in CI).
- Frontend: 26 files, 81 tests passed.
- Privacy audit: 0 findings across 48 router/service files.
- Alembic: single head `0069_redact_tester_flags`.
- Supply chain: 143 files and 222 labs; signed lock verified.
- Links: 362 Markdown files, no broken links; publication audit clean.
- CI and Quality checks: green on `main` at `4ecf90ff` before the version bump.

## Residual risks

- RB-06 remains partial: the wiki CSP still needs `unsafe-inline` for MkDocs Material; a split origin or nonce pipeline is the durable fix.
- RB-07/08/09 (TLS renewal, backup encryption, external monitoring) remain operational items.
- HS-09: the Peer Manager still runs as root; the capability drop needs a host test.
- The licence stays PolyForm Noncommercial until the upstream author gives written permission.
