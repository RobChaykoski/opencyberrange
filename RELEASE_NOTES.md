# OpenCyberRange 1.0.0

Released: 4 November 2026

OpenCyberRange 1.0 is the first supported self-hosted teaching release. It is intended for instructors and platform administrators running hands-on cybersecurity exercises on their own infrastructure.

## Highlights

- **Certificates and recognition**: selectable certificate designs, QR verification, SWOCTS trust marks, scoped achievements, and course achievement summaries.
- **Competitions**: opt-in events, event leaderboards, competition-specific achievements, and multi-sponsor recognition with Gold, Silver, and Bronze tiers.
- **Profiles and accessibility**: profile photos, avatar borders, improved keyboard and screen-reader behaviour, and a cleaner completion matrix.
- **Privacy and resilience**: personal-data export, audited erasure, persistent daily database snapshots, and a snapshot calendar that matches the files on disk.
- **Safer input handling**: Unicode-aware passwords, validated image uploads, and normalised course invite codes.

## Upgrade notes

1. Take a database snapshot before upgrading.
2. Pull the `v1.0.0` tag or the matching `main` commit.
3. Rebuild the backend and frontend images.
4. Start the stack and verify `/health` reports `version: 1.0.0`.
5. Confirm the Backups tab lists the pre-upgrade snapshot and that a new daily snapshot can be collected.

The new `backups_data` volume is created automatically. Existing snapshots that were stored only inside the old backend container were not persistent and cannot be recovered after the container is replaced.

## Supported scope

- Self-hosted Docker Compose deployments.
- WireGuard-based learner access, with optional WSTunnel deployments.
- Current supported runtime versions are recorded in `versions.yaml`.

## Known limitations

- Backups are retained for 30 days by default. Configure `OCR_BACKUP_RETENTION_DAYS` to change this.
- Snapshot encryption at rest is an operator responsibility; store snapshots on encrypted storage.
- Sponsor logos are stored in the database as resized image data, capped at 256 KB.

## Verification

Release verification for 1.0.0 includes:

- Backend test suite.
- Frontend lint and production build.
- Test-stack deployment.
- Production upgrade from the previous supported commit.
- Snapshot collection and container-recreation persistence check.
- Restore drill using the generated snapshot.
