# Validation report

**Release:** 5.17.1
**Commit:** `7c0d0603` (signed tag `v5.17.1`)
**Date:** 16 November 2026

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
- Clean local test database: **898 passed, 0 failed, 0 skipped**.
- Security configuration tests cover placeholder secrets, production
  environment, strict authorization, and WireGuard key requirements.
- Consent tests cover explicit opt-in for Cyber DNA, Cyber GPS, and portfolio.
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

- Lab validation: **191 labs, 0 failed checks** (192 entries including `_summary`).
- Lab metadata: schema validation passed in CI.
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
| `/api/version` | `5.17.1` |
| `/health` | `200` |
| Alembic | `0040_settings_change_control` |
| Registered labs | `191` |
| Admin release status | `current` / `v5.17.1` |
| Backup | `ocr-backup-20261116-181526.dump` |
| Restore drill | **PASSED** |

## Known gaps

- Independent penetration testing is **not yet commissioned**. See
  [Independent security testing](INDEPENDENT-SECURITY-TESTING.md).
- Tenant isolation is enforced on the nine RLS tables but not yet on every
  legacy learner-owned table. See [Tenant isolation status](TENANT-ISOLATION-STATUS.md).
- Production cutover has not run; `deployment_mode=development` and
  `data_collection_mode=sample` remain. See
  [Production deployment statement](PRODUCTION-DEPLOYMENT-STATEMENT.md).
- The ATT&CK Navigator iframe requires internet access to
  `mitre-attack.github.io`; the panel fallback is present when the origin is
  blocked.

## Reproduce

Run the CI workflows or the commands above on a clean checkout at the release
commit. A result is only comparable when the commit, database state, and test
environment are recorded.
