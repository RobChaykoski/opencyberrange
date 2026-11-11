# Deployment runbook

Operational commands for the two deployed environments.

| Environment | Address | Login / deploy user | Repository | Compose directory |
|---|---|---|---|---|
| Production | `172.16.16.41` / `https://ctfd.swocts.com` | `rchaykoski` | `~/opencyberrange` | `~/opencyberrange/platform` |
| Development | `172.16.16.44` | `ocrv2` | `~/opencyberrange` | `~/opencyberrange` |

The canonical repository is `RobChaykoski/opencyberrange`. Production tracks it
as `canonical/main`; its `origin` remote points at the same repository.

## Pull the reviewed tree

Production:

```bash
cd ~/opencyberrange
git fetch canonical
git pull --ff-only canonical main
```

Development:

```bash
cd ~/opencyberrange
git pull --ff-only origin main
```

## Backend and frontend

Production compose files:

```bash
cd ~/opencyberrange/platform
docker compose \
  -f docker-compose.prod.yml \
  -f docker-compose.adopt.yml \
  -f docker-compose.override.yml \
  build backend frontend

docker compose \
  -f docker-compose.prod.yml \
  -f docker-compose.adopt.yml \
  -f docker-compose.override.yml \
  up -d backend frontend
```

Development uses the root compose files:

```bash
cd ~/opencyberrange
docker compose build backend frontend
docker compose up -d backend frontend
```

The development backend code is bind-mounted from `~/opencyberrange/backend`.
After pulling, copy the changed backend source into that directory before a
restart. Production bakes the code into the image and always needs a rebuild.

## Prebuild lab images

New or changed labs must be built on the host. On-demand builds are disabled.

```bash
cd ~/opencyberrange
bash scripts/prebuild-labs.sh --lab <lab-slug> --force
```

Disk warning: production is below the 60 GB prebuild recommendation. Do not run
`docker image prune -a`; it would delete the prebuilt lab images.

## WireGuard client-pool route

Existing hosts:

```bash
sudo bash scripts/fix-wireguard-client-route.sh
```

The route is `10.255.0.0/16 dev wg0`, added at runtime and persisted in
`PostUp`/`PostDown`.

## Level quiz banks

The quiz runtime is part of the backend. Seed or update the Beginner quiz banks
inside the backend container:

```bash
docker exec -e PYTHONPATH=/app ocr-backend \
  python -m app.scripts.seed_level_quizzes
```

The script is idempotent and replaces the questions for each level while
leaving attempts intact.

## Health and status

```bash
curl -sk https://127.0.0.1/health
curl -sk https://127.0.0.1/api/version
docker ps --filter name=ocr-backend
docker logs --since 5m ocr-backend
```

From the operator workstation, refresh the documented status page:

```bash
python scripts/status-dashboard.py --config docs/status-hosts.json
```

## Regression checks

Run these from the operator workstation against a deployment. Each writes JSON
and screenshots to `UI_ARTIFACT_DIR` (default names vary by script).

| Check | Script | Needs |
|---|---|---|
| Deployment smoke | `scripts/ui-smoke.mjs` | `UI_BASE_URL`, `UI_SMOKE_TOKEN` or `UI_SMOKE_USERNAME`/`UI_SMOKE_PASSWORD` |
| Learning gating | `scripts/ui-learning-smoke.mjs` | `UI_BASE_URL`, `UI_USERNAME`, `UI_PASSWORD` |
| Exercise workspace | `scripts/ui-workspace-regression.mjs` | `UI_BASE_URL`, student and instructor credentials |
| Public verification | `scripts/ui-verify-public.mjs` | `UI_VERIFY_URLS` (public certificate URLs) |

`UI_PLAYWRIGHT_PATH` accepts a package name, a package path, or a `file://` URL.
On a workstation with Edge installed, set `UI_BROWSER_EXECUTABLE` to the Edge
executable and skip the Playwright browser download.

Backend unit tests for the release fixes:

```bash
cd platform/backend
python -m pytest tests/test_target_ip_reveal.py tests/test_lab_network_cleanup.py \
  tests/test_event_certificate_pdf_layout.py
```

Static checks used by CI:

```bash
python scripts/check-nginx-security-headers.py
python scripts/check-doc-assets.py
python scripts/check-links.py Manual-Lite docs Workbook --mkdocs
```

## Release evidence

Record verification results in `docs/UI-VERIFICATION.md`. The repeatable
learning smoke is `scripts/ui-learning-smoke.mjs` (quiz visibility and level
certificates).
