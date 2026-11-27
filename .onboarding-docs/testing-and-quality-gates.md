# Testing and quality gates

The project uses fast local checks, a database-backed backend suite, a frontend
unit suite, content validators, and several CI workflows. Run the narrowest
check that proves your change, then the full gate before you open a pull
request.

## Backend tests

The backend suite lives in `platform/backend/tests/`. It uses an ephemeral
PostgreSQL when `TEST_DATABASE_URL` is set; DB-backed tests skip cleanly when it
is not.

```bash
cd platform/backend
python -m pytest -q
```

On Windows with the repository virtual environment:

```powershell
cd platform/backend
..\..\.venv\Scripts\python.exe -m pytest -q -o addopts=""
```

Set a disposable database for the full suite:

```bash
export TEST_DATABASE_URL="postgresql://ocr_test:ocr_test@127.0.0.1:5432/ocr_test"
python -m pytest -q
```

Useful focused runs:

```bash
python -m pytest tests/test_auth.py tests/test_jwt_validation.py tests/test_login_throttle.py -q
python -m pytest tests/test_authorization_matrix.py tests/test_idor_matrix.py tests/test_horizontal_privilege.py -q
python -m pytest tests/test_consent_revocation.py tests/test_privacy.py -q
python -m pytest tests/test_zip_upload_hardening.py tests/test_input_safety.py -q
```

The pytest configuration is `platform/backend/pytest.ini`. Coverage is enabled
there; pass `-o addopts=""` to turn it off for a quick local loop.

## Frontend tests and build

```bash
cd platform/frontend
npm ci
npm run lint
npm test
npm run build
```

Vitest runs the `src/**/*.test.js` files. The production build is the same Vite
build used in the frontend image; a broken import or template fails here.

## Lab and content validation

```bash
python scripts/validate-lab.py --all
python scripts/validate_lab_metadata.py
python scripts/validate-framework-map.py
python scripts/validate-competency-contracts.py
python scripts/validate-rubrics.py
python scripts/lab_harness.py --validate-all
python scripts/check-lab-freshness.py
python scripts/audit-publication.py --summary
python scripts/audit-release6-coverage.py --fail-on-gaps
```

When you add or change a lab:

```bash
python scripts/generate-lab-manifests.py
python scripts/generate-workbook-coverage.py
python scripts/generate-competency-contracts.py
python scripts/generate-competency-review-queue.py
python scripts/generate-lab-outcomes.py
python scripts/generate-nice-lab-mappings.py
```

Run the matching `--check` variants before committing. Generated files must be
regenerated, not edited by hand.

## Documentation checks

```bash
python scripts/documentation_map.py --check
python scripts/check-links.py --mkdocs
python scripts/check-data-dictionary.py
python scripts/check-mojibake.py
python scripts/check-external-images.py
python scripts/check-safe-links.py
```

The onboarding docs under `.onboarding-docs/` are Markdown and are included in
the link check when you pass the docs path explicitly:

```bash
python scripts/check-links.py .onboarding-docs
```

## Supply chain and release gates

```bash
python scripts/supply_chain.py --check
python scripts/supply_chain.py --check \
  --signature supply-chain.lock.json.asc \
  --gpg-public-key docs/release-signing-key.asc \
  --gpg-fingerprint 68A817762C831475F00DB54E775050A4C4921814
python scripts/generate-integrity-manifest.py
```

After a content change, the lock must be updated and signed as part of the
release procedure. Do not sign a lock for a change you are not releasing.

## Blackbox security and privacy suite

The Karate suite runs against a Docker deployment over an SSH tunnel. It creates
disposable identities, writes a runtime fixture, runs the tests, and deletes the
identities.

```powershell
cd security-tests/karate
.\run-security-tests.ps1 -Tags '@security'
```

See [Security tests](security-tests/README.md) for prerequisites, environment
variables, and cleanup behaviour.

## CI workflows

| Workflow | What it proves |
|---|---|
| `ci.yml` | backend tests, frontend tests/build, container builds |
| `quality.yml` | supply-chain lock, generated records, lab validation, docs links and builds, licences, CSP, external images |
| `codeql.yml` | static analysis |
| `trivy.yml` | image and dependency scanning |
| `scorecard.yml` | supply-chain posture |
| `ubuntu-next.yml` | next Ubuntu LTS candidate |
| `docs-publish.yml` | manual publishing |
| `security-delta.yml` | security-relevant diff review |

Run the local equivalents in `quality.yml` before pushing. The workflow is the
source of truth for the exact commands.

## What "done" means

A change is ready when:

- the narrow tests for the touched subsystem pass;
- generated records and the supply-chain lock are current;
- the link check and the documentation map pass if docs changed;
- the frontend build and lint pass if the UI changed;
- the lab validator and harness pass if a lab changed;
- the security suite passes if authentication, authorization, uploads, or
  privacy boundaries changed;
- the pull request states the evidence, not just the intention.
