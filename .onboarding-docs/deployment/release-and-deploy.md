# Release and deploy

The release procedure is deliberately strict: a signed tag, a locked supply
chain, a reproducible integrity manifest, and a verified deployment. Do not edit
a running host to work around the process.

## 1. Prepare the version

Bump all version locations together:

- `versions.yaml` (`platform.version`, `release.version`)
- `platform/backend/app/version.py`
- `platform/frontend/package.json`
- the manual and release pages that print the version

Update `CHANGELOG.md` and the release scope or deliverables page.

## 2. Regenerate generated records

Run the generators for anything you changed:

```bash
python scripts/generate-competency-contracts.py
python scripts/generate-competency-review-queue.py
python scripts/generate-lab-outcomes.py
python scripts/generate-nice-lab-mappings.py
python scripts/generate-lab-manifests.py
python scripts/generate-workbook-coverage.py
python scripts/generate-curriculum-docs.py
python scripts/generate-framework-docs.py
python scripts/generate-rbac-matrix.py
```

Then run the matching `--check` commands. Generated files are never hand-edited.

## 3. Lock and sign the supply chain

```bash
python scripts/supply_chain.py --update
python scripts/generate-integrity-manifest.py
python scripts/supply_chain.py --update
python scripts/generate-integrity-manifest.py
```

Run the integrity manifest twice; the hash must not change. Then sign the lock:

```bash
gpg --detach-sign --armor supply-chain.lock.json
python scripts/supply_chain.py --check \
  --signature supply-chain.lock.json.asc \
  --gpg-public-key docs/release-signing-key.asc \
  --gpg-fingerprint 68A817762C831475F00DB54E775050A4C4921814
```

The exact key and fingerprint are in the release procedure. Do not sign a lock
for a change you are not releasing.

## 4. Tenant isolation check

On the development host:

```bash
docker exec -i ocr-backend python - < scripts/check-tenant-isolation.py
```

Confirm `PASSED` before tagging.

## 5. Tag and push

```bash
git tag -s vX.Y.Z -m "Release X.Y.Z"
git push origin main --tags
```

The tag is the release. CI must pass before the tag is considered valid.

## 6. Deploy on the host

```bash
bash scripts/deploy-inplace.sh --dry-run
bash scripts/deploy-inplace.sh
```

The script uses `platform/docker-compose.prod.yml`, plus `adopt` and `override`
if present. It builds images, applies migrations, recreates services, and checks
health.

Verify:

```bash
ssh <production-host> "curl -fsS http://127.0.0.1:8000/api/version"
docker compose --env-file .env -f platform/docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:8000/health
```

## 7. Record the deployment

Update:

- `docs/PRODUCTION-DEPLOYMENT-STATEMENT.md`
- `docs/RELEASE-X.Y.Z-DELIVERABLES.md`
- the project overview pack if the API or infrastructure changed

## 8. Rollback

The previous images are tagged before a deploy, for example
`opencyberrange-backend:pre-v5.56.1` and `ocr-frontend:pre-v5.56.1`. To roll
back, deploy the previous signed tag and its images, then verify health and the
database migration state. A schema migration may be forward-only; check the
migration notes before rolling back the application.

## 9. Post-deploy checks

- [ ] `/api/version` reports the new release on every host.
- [ ] Health endpoint is green.
- [ ] Admin System Health is green.
- [ ] Lab discovery count matches the release.
- [ ] A learner can log in and start one lab in a smoke course.
- [ ] Backups ran after the deploy.
- [ ] Security events and monitoring are receiving data.
- [ ] The deployment statement has the evidence hash.

## Related

- [Releases](../../docs/RELEASES.md)
- [Release 6 scope](../../docs/RELEASE-6-SCOPE.md)
- [Production deployment statement](../../docs/PRODUCTION-DEPLOYMENT-STATEMENT.md)
- [Deployment runbook](../../docs/DEPLOYMENT-RUNBOOK.md)
- [Supply chain](../../docs/SUPPLY-CHAIN.md)
