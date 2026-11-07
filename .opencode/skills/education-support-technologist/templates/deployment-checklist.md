# Deployment checklist

Copy this into the change ticket or operations log.

## Change

- Date/time:
- Operator:
- Platform:
- Target version/commit:
- Current version/commit:
- Reason for change:
- Change window:
- Approved by:

## Pre-flight

- [ ] Teaching calendar checked; no class or assessment conflict.
- [ ] Release note read.
- [ ] Migrations identified.
- [ ] New environment variables identified.
- [ ] Disk and memory checked.
- [ ] Public/private port changes checked.
- [ ] Rollback owner and method confirmed.

## Backup

- [ ] Database dump created and non-zero.
- [ ] `.env` and Compose configuration backed up.
- [ ] Uploads, workbook/wiki volume, and erasure ledger backed up.
- [ ] TLS and VPN configuration backed up.
- [ ] Backup copied off the host.
- [ ] Restore path documented.

## Apply

- [ ] `git pull` completed.
- [ ] Diff reviewed; no secrets or learner exports included.
- [ ] Images rebuilt or approved images pulled.
- [ ] Services started with `docker compose up -d`.
- [ ] Migration or seed command run only if documented.

## Verify

- [ ] Health endpoint passes.
- [ ] Test student login passes.
- [ ] Test instructor login passes.
- [ ] Dashboard and course list load.
- [ ] One lab launches and stops.
- [ ] One report page loads.
- [ ] One export completes and records a reason.
- [ ] Administrator page loads.
- [ ] Logs show no repeated errors.
- [ ] Footer shows the expected version.

## Close-out

- [ ] Version/commit recorded.
- [ ] Commands and checks recorded.
- [ ] Backup location recorded.
- [ ] Teaching team notified.
- [ ] Follow-up items assigned.
- [ ] Rollback decision recorded (not needed / completed).

## Rollback (if needed)

- Trigger:
- Code version restored:
- Backup restored:
- Verification repeated:
- Follow-up:
