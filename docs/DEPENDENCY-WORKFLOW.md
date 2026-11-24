# Dependency and image workflow

The platform pins exact backend versions and digest-pinned base images. This
page defines the cadence so upgrades are small, tested, and signed.

## Weekly

The `dependency-audit` workflow runs on Mondays and on pull requests:

- `pip-audit -r platform/backend/requirements.txt`
- `npm audit --omit=dev`
- `python scripts/check-dependency-currency.py`

The audit job is intentionally non-blocking while the baseline exceptions are
open. The currency report lists core backend packages that are behind PyPI.

## Monthly patch wave

1. Create a branch and update only patch/minor versions in
   `platform/backend/requirements.txt` and `versions.yaml`.
2. Run the full backend suite and frontend tests.
3. Rebuild the backend and run the lab harness for one network, one ICS, and one
   RangeBox lab.
4. Refresh and sign the supply-chain lock.
5. Release as a patch/minor version; do not combine with a database major
   upgrade.

```bash
cd platform/backend
pip install -r requirements.txt
pytest -q --no-cov tests
cd ../..
python scripts/supply_chain.py --update
gpg --detach-sign --armor supply-chain.lock.json
```

## Quarterly base-image refresh

1. Refresh the pinned digests in the Dockerfiles and `versions.yaml`:
   `python:3.13-slim`, `node:22-alpine`, `nginx:alpine`, `alpine:3.20`.
2. Rebuild backend, frontend, `ocr-lab/netprobe`, and the tester image.
3. Run Trivy and the image scan workflow.
4. Validate a lab spawn, a RangeBox session, and the workbook reader.

Do not move to a new major runtime in a base-image refresh.

## Annual or planned upgrades

- PostgreSQL 15 → 17: separate maintenance window, dump/restore or `pg_upgrade`,
  restore drill, RLS role check.
- Python 3.13 → 3.14: separate compatibility wave.
- Node 22 → 24: separate frontend tooling wave.
- Ubuntu 24.04 → 26.04: host migration wave.

Each major upgrade gets its own release and rollback plan. Do not bundle them.

## Current exceptions

The weekly audit is non-blocking until the known exceptions are cleared. Record
any exception with an owner and expiry in the release notes or
`docs/SUPPORTED-VERSIONS.md`.
