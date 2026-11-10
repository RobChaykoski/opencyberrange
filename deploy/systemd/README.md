# Scheduled database integrity checks

These units run the read-only OpenCyberRange integrity checks once a day and
write the evidence outside the database.

## Install

1. Put the signing key and any deployment overrides in a root-only env file:

   ```bash
   sudo install -d -m 700 /etc/opencyberrange
   sudo sh -c 'umask 077; printf "DB_INTEGRITY_KEY=%s\n" "$(openssl rand -hex 32)" > /etc/opencyberrange/integrity.env'
   ```

2. Adjust the checkout path in `ocr-db-integrity.service` if it is not
   `/home/ocr/opencyberrange`.

3. Install and enable the units:

   ```bash
   sudo cp deploy/systemd/ocr-db-integrity.service \
           deploy/systemd/ocr-db-integrity.timer \
           deploy/systemd/ocr-db-integrity-alert@.service \
           /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now ocr-db-integrity.timer
   systemctl list-timers ocr-db-integrity.timer
   ```

4. Run once immediately to validate the setup:

   ```bash
   sudo systemctl start ocr-db-integrity.service
   sudo systemctl status ocr-db-integrity.service
   ls -l /var/lib/ocr-integrity/
   ```

## What it runs

- `--quality` — data-quality audit; a critical finding fails the unit.
- `--ledger` — append-only ledger chain; a broken chain fails the unit.
- `--checksum` — table checksums and database fingerprint.
- On Sunday (ISO weekday 7): a signed manifest when `DB_INTEGRITY_KEY` is set.

The wrapper is `scripts/db-integrity-check.sh`. It uses `flock`, so a manual run
cannot overlap the timer.

## Evidence retention

Evidence is written to `/var/lib/ocr-integrity` by default and pruned after 90
days. Copy it to a separate host or backup target. A manifest stored only on the
database host is not tamper evidence.

The admin portal's **System → Integrity** tab shows the live ledger summary.
Full chain, checksum, and quality verification stay on this host schedule.

## Alerting

The service uses `OnFailure=ocr-db-integrity-alert@%n.service`. The shipped
alert unit writes to syslog; replace its `ExecStart` with your monitoring
webhook or point your existing alerting at `ocr-db-integrity.service`.

## Overrides

The wrapper honours:

| Variable | Default | Meaning |
|---|---|---|
| `OCR_PLATFORM_DIR` | parent of the script | Checkout containing `scripts/database_integrity.py` |
| `OCR_BACKEND_CONTAINER` | `ocr-backend` | Backend container name |
| `OCR_INTEGRITY_EVIDENCE_DIR` | `/var/lib/ocr-integrity` | Evidence output |
| `OCR_INTEGRITY_RETENTION_DAYS` | `90` | Evidence retention |
| `OCR_INTEGRITY_MANIFEST_DAY` | `7` | ISO weekday for the signed manifest |
| `OCR_INTEGRITY_LOCK` | `/run/ocr-db-integrity.lock` | Single-run lock |
| `DB_INTEGRITY_KEY` | unset | HMAC key for signed manifests |
