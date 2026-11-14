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

### Backup volume ownership

The `backups_data` volume must be writable by the backend UID `10001`. After a
fresh volume, a host migration, or a restore that recreates the volume:

```bash
docker exec -u root ocr-backend chown -R 10001:10001 /app/backups /workbook
```

Verify with:

```bash
docker exec ocr-backend sh -c 'touch /app/backups/.perm-test && rm /app/backups/.perm-test'
```

Without this, **Create snapshot** returns 500 with
`pg_dump: could not open output file ... Permission denied`.

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

## Backups

Production runs `scripts/backup-production.sh` daily at 03:15 UTC from the
deploy user's crontab. It writes a validated custom-format dump
(`ocr-backup-<stamp>.dump`), the erasure ledger, the platform `.env`, and a
SHA-256 file to `~/backups`, pruning only its own files after 14 days.

The cron sets
`BACKUP_REMOTE=ocr-offsite:/home/ocrv2/backups/prod` and
`BACKUP_GPG_RECIPIENT=1082980711C1246F3601434C84F6ACCD1A0E0CB0`. The
`ocr-offsite` SSH alias on the production host uses
`~/.ssh/ocr_backup_ed25519`, whose public key is authorized on development.
Sensitive off-host files (dump, erasure ledger, platform env) are encrypted to
the **OCR Offsite Backup** key before transfer; production holds only the public
key, and the private key is kept in the release operator's keyring. The local
plaintext dump is retained for the weekly drill. Development is an interim
off-host target and must be replaced by institutional storage before it is
relied on for disaster recovery. Prune the off-host copy under the institution's
retention policy.

Restore from the off-host copy:

```bash
scp ocr-dev:/home/ocrv2/backups/prod/ocr-backup-<stamp>.dump.gpg .
scp ocr-dev:/home/ocrv2/backups/prod/ocr-backup-<stamp>.dump.sha256 .
gpg --decrypt --output ocr-backup-<stamp>.dump ocr-backup-<stamp>.dump.gpg
sha256sum -c ocr-backup-<stamp>.dump.sha256   # compare the hash only
```

Then restore into a scratch database and compare counts before touching live
data. Rotating the backup key requires importing the new public key on
production, updating `BACKUP_GPG_RECIPIENT`, and keeping the old private key
long enough to read existing off-host copies.

### Backup transports

Any combination of these can be set; each receives the encrypted set. Without
`BACKUP_GPG_RECIPIENT` the script refuses to copy off-host unless
`BACKUP_ALLOW_PLAINTEXT=1` is explicitly set.

| Variable | Transport | Notes |
|---|---|---|
| `BACKUP_REMOTE` | rsync over SSH | Current production path (`ocr-offsite:/home/ocrv2/backups/prod`); SSH encrypts transit |
| `BACKUP_NFS_DIR` | NFS | Path to an **already mounted** directory. Prefer NFSv4 with Kerberos; the mounted filesystem must be writable by the deploy user |
| `BACKUP_SMB_URL` | SMB via curl | `smb://172.16.16.8/Backups/OCR-Export-Backup/` with `BACKUP_SMB_NETRC`; prefer SMB3 signing/encryption |
| `BACKUP_RCLONE_REMOTE` | Any rclone remote | S3/WebDAV/SFTP; use an rclone `crypt` remote or provider-side encryption |
| `BACKUP_COPY_CMD` | Custom executable | Receives each encrypted file path; the escape hatch for an institutional tool |

NFS/SMB/rclone all carry the same GPG-encrypted files, so transport encryption
is a second layer, not the only one. Mounting NFS/CIFS requires root and is done
by the host operator; the backup script itself never mounts anything.

For SMB, create `~/.ocr-smb-netrc` (mode 600):

```text
machine 172.16.16.8 login <service-account> password <secret>
```

and set `BACKUP_SMB_URL='smb://172.16.16.8/Backups/OCR-Export-Backup/'` plus
`BACKUP_SMB_NETRC="$HOME/.ocr-smb-netrc"` in the backup cron. The NAS copy
stays disabled until that service account is provided; the dev off-host copy
remains the active secondary target.

```bash
crontab -l | grep -E 'backup-production|restore-drill'
bash scripts/backup-production.sh          # run now
bash scripts/restore-drill.sh              # restore newest dump to a scratch DB
```

`restore-drill.sh` never touches the live database: it restores into a
`labdb_restore_drill_*` database, compares row counts for the core tables, and
drops it. Run it after installing or changing the timer, and before a release
that includes a migration. Copy `~/backups` off-host (set `BACKUP_REMOTE` to an
rsync target to do it from the script) so a host failure does not take the
database and its backups together.

## Monitoring

`scripts/monitor-deployment.sh` runs every 10 minutes from the deploy user's
crontab and checks `/api/version`, the backend health probe, the 8443 workbook
origin, container health, free disk, local and off-host backup age, and the TLS
certificate's 30-day expiry window. It writes
`~/.local/state/ocr-monitor/status.json` and logs to
`~/.local/state/ocr-monitor/cron.log`.

Set `ALERT_WEBHOOK_URL` (Slack-compatible JSON `{"text": ...}`) and/or
`ALERT_COMMAND` (an executable that receives the failure message as its first
argument) in `~/.ocr-monitor.env` to receive failures. Without either, failures
are still visible in `status.json`, `last-failure.txt`, and `cron.log`.
`DISK_MIN_GB` and `BACKUP_MAX_HOURS` override the defaults in that file.

```bash
bash scripts/monitor-deployment.sh
cat ~/.local/state/ocr-monitor/status.json
cat ~/.local/state/ocr-monitor/last-failure.txt 2>/dev/null
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

## Release 5 deployment notes

Release 5 adds LTI 1.3, per-student accommodations, minor consent/retention,
the tabbed workspace, and a dedicated workbook origin. Before deploying:

1. Take a database backup and copy the erasure ledger.
2. Confirm TCP **8443** reaches the frontend. UFW is disabled on the current
   host and the port resets rather than drops, so no host firewall change is
   required. Workbooks are served from `https://<host>:8443`.
3. After migrations, set the `wiki_origin` platform setting to
   `https://<host>:8443`.
4. Build with `PLATFORM_VERSION=5` and confirm `/api/version`.
5. Apply migrations `0015`–`0025` and confirm `alembic current` reports
   `0025_review_requests`.

Production compose build and deploy:

```bash
cd ~/opencyberrange/platform
docker compose -f docker-compose.prod.yml -f docker-compose.adopt.yml \
  -f docker-compose.override.yml build backend frontend
docker compose -f docker-compose.prod.yml -f docker-compose.adopt.yml \
  -f docker-compose.override.yml up -d
docker exec ocr-backend sh -c 'cd /app && alembic -c alembic.ini upgrade head'
```

Verify version, health, labs, the workspace tabs, the 8443 workbook, and the
LTI admin panel. Keep the previous image tags and the pre-deploy database dump
for rollback. See [`RELEASE-5-PRODUCTION-READINESS.md`](RELEASE-5-PRODUCTION-READINESS.md).

## Release evidence

Record verification results in `docs/UI-VERIFICATION.md`. The repeatable
learning smoke is `scripts/ui-learning-smoke.mjs` (quiz visibility and level
certificates).
