# Validation report

**Release:** 5.17.7
**Commit:** `a7a9509a` (signed tag `v5.17.7`)
**Date:** 17 November 2026

This is the reproducible validation record for the current release. Commands
are run from the repository root unless noted.

## CI

| Workflow | Result |
|---|---|
| CI (backend, frontend, compose, docs/security regression) | **success** |
| Quality checks | **success** |
| CodeQL | **success** |
| Trivy security scan | **success** |
| OpenSSF Scorecard | **success** |
| Security delta review | **success** |
| Publish documentation | **success** |

CI run: `https://github.com/RobChaykoski/opencyberrange/actions`

## Backend

```bash
cd platform/backend
TEST_DATABASE_URL=postgresql://... pytest -q
ruff check app
```

- CI backend job: **success**.
- Clean local test database: **908 passed, 0 failed, 0 skipped**.
- Security configuration tests cover placeholder secrets, production
  environment, strict authorization, and WireGuard key requirements.
- Consent tests cover explicit opt-in for Cyber DNA, Cyber GPS, and portfolio.
- Password prompts (login, re-authentication, change-password, account deletion,
  admin reset, MFA disable, and the cutover gate) accept the correct password
  and reject a wrong password. Oversized, control-character, and
  injection-shaped input is rejected without echoing the value.
- The API manual and lab-outcomes generators pass their `--check` drift tests.

## Frontend

```bash
cd platform/frontend
npm ci
npm run lint
npm test
npm run build
```

- Tests: **6 passed**.
- Build: **success**.
- Lint: **0 errors**, warnings tracked but not release-blocking.

## Labs and metadata

```bash
python scripts/validate-lab.py --all --json
python scripts/validate_lab_metadata.py --quiet
python scripts/check-malware-governance.py
python scripts/check-external-datasets.py
python scripts/check-links.py Manual-Lite docs Workbook --mkdocs
```

- Lab validation: **210 labs, 0 failed checks** (211 entries including `_summary`).
- Lab metadata: schema validation passed in CI.
- Tester manifests: **210**, current against the lab definitions.
- Discovery: the CLI creates missing tracks/levels before scanning; a clean
  database import produced **210 labs**. The seed defines level 11 for the
  `windows` and `web` tracks.
- Tenant RLS: **25 tables** enforced; the regression test asserts the column,
  forced RLS, and four policies, and probes two newly migrated learner tables
  across two institutions.
- Live harness: all **19 new pathway labs** passed one clean run after the LDAP
  startup and LDIF-wrap fixes. The full 210-lab, three-run harness remains.
- Workbook coverage: **201 of 210** labs after the two pathway chapters. All 19
  pathway pages carry the required Analysis Questions, and each pathway awards a
  range-wide completion badge (`ad_pathfinder`, `appsec_architect`).
- Malware governance: passed.
- External dataset registry: passed.
- Documentation links: passed after the API manual link fix.

## Supply chain

```bash
python scripts/supply_chain.py --check \
  --signature supply-chain.lock.json.asc \
  --gpg-public-key docs/release-signing-key.asc
```

- Signed lock matches the release tree.
- Trivy image and filesystem scan: **success**.
- SBOM and third-party notices are present.

## Deployment smoke

| Check | Result |
|---|---|
| `/api/version` | `5.17.7` |
| `/health` | `200` |
| Alembic | `0041_tenant_rls_legacy` |
| Content refresh | `3379f27f` (workbook 201/210, live harness 19/19) |
| Registered labs | `210` (170 public, 40 course-scoped) |
| Users | `87` (47 human + 40 stress-test) |
| Courses | `2` |
| Admin release status | `current` / `v5.17.7` |
| Cutover | `deployment_mode=production`, `data_collection_mode=production` |
| Backup | `ocr-backup-20261117-035821.dump` |
| Restore drill | **PASSED** (87 users, 2 courses, 210 labs, 41 enrollments, 124 completions, 463 achievements) |
| Live password check | correct login/reauth/change = `200`; wrong/oversized/newline = `401` |

## Known gaps

- Independent penetration testing is **not yet commissioned**. See
  [Independent security testing](INDEPENDENT-SECURITY-TESTING.md).
- Tenant isolation is enforced on **25** learner-owned tables. Authentication,
  consent, course-content, and platform-operation tables are classified rather
  than force-scoped. See [Tenant isolation status](TENANT-ISOLATION-STATUS.md).
- The manual screenshots use synthetic data but were captured on an older build
  (footer `v5`, 149 exercises). A refresh needs demo credentials; see
  [Manual screenshots](MANUAL-SCREENSHOTS.md).
- Production cutover is **complete** (2026-11-16 19:21:54 UTC, ticket `123456`,
  approver Robert Chaykoski, evidence hash `4f76c44e…`). See
  [Production deployment statement](PRODUCTION-DEPLOYMENT-STATEMENT.md).
- `smoke_tester` and `tester` remain in production by operator decision.
- The ATT&CK Navigator iframe requires internet access to
  `mitre-attack.github.io`; the panel fallback is present when the origin is
  blocked.

## Reproduce

Run the CI workflows or the commands above on a clean checkout at the release
commit. A result is only comparable when the commit, database state, and test
environment are recorded.
