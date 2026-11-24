# Release 5.50.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.50.0` |
| Signed tag | `v5.50.0` |
| Release commit | Pending tag |
| Alembic | `0067_course_content_rls` (no migration) |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |

## Tenant isolation

| Deliverable | Detail |
|---|---|
| Control audit | `scripts/check-tenant-isolation.py` checks 47 tables and probes as a foreign tenant |
| Audit result | PASS on development and production, zero leaked rows |
| Pilot runbook | `docs/TWO-TENANT-PILOT.md` with setup, checks, rollback, and acceptance |
| API probe | `scripts/check-tenant-pilot-api.py` for two-token course/evidence/catalogue/admin checks |
| Classification | `users` recorded as the tenant source outside RLS by design |
| Consent design | ADR 0010, gated on the pilot |

## Competency review

| Deliverable | Detail |
|---|---|
| Campaign plan | `docs/reviews/COMPETENCY-REVIEW-CAMPAIGN.md` |
| Status | `25/215` reviewed, `190` pending |
| First batch | 25 legacy drafts, now seeded on production |
| Ranking | 30 highest-use pending labs from production usage |
| Gate | Offline `--check` still fails closed until signatures exist |

## Host agent

| Deliverable | Detail |
|---|---|
| Harness | `scripts/check-labd-harness.sh` creates a disposable container and exercises status/stop |
| Result | PASS on development |
| Production | Agent is not installed; stop stays opt-in |

## Threat awareness

| Deliverable | Detail |
|---|---|
| Snapshot | Live RansomLook aggregate: `291` posts in `7` days, `15` groups |
| Privacy | Totals and group counts only; no victim, link, crypto, or peer data |
| Sample banner | Removed for the ransomware section |
| FireHOL | Still the labelled sample until a local GeoIP database is available |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,196 passed` expected (no backend change) |
| Frontend tests | `38 passed` expected |
| Alembic safety guard | Single head `0067_course_content_rls` |
| Tenant audit | PASS, 47 tables, 0 leaks |
| Labd harness | PASS |
| Ransomware snapshot | Validated as `snapshot`, `291` posts, `15` groups |
| Production drift | `0` expected |
| Production health | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The threat map remains a labelled sample until an operator installs a local
  GeoIP database.
- The 190 pending contracts still need subject-matter sign-off.
- `ocr-labd` is validated on development only; no production cutover.
- Multi-tenant use remains deferred until the pilot and consent wave pass.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] CI integrity gate passes on the release commit.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Ransomware section reports `snapshot` mode on production.
- [ ] Tenant audit passes on production.
- [ ] Production drift is `0`.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill and restore-drift gate at `0` passed.
- [ ] Rollback images retained.
