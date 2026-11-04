# OpenCyberRange 2.0 development

Status: development line. This is not a GA release and may change before 2.0.0.

## Added in this build

- **Learning hours:** tracked time on completed exercises, plus bounded session
  time for started exercises without a completion, shown privately to learners
  and as course and cross-course aggregates.
- **Exercise reactions:** a one-tap Like/Dislike control while an exercise is
  open, reported as aggregate likes, dislikes, and positive rate. Learner names
  are not shown in the reports.
- **Engagement badges:** global achievements for 1, 5, 15, and 30 tracked
  learning hours, and for 3, 7, and 30 consecutive sign-in days.
- **Profile email consent:** a Privacy and data control for optional account
  email, with PIPEDA withdrawal language and an auditable consent version and
  timestamp.
- **Reporting exports:** cross-course Reports can be downloaded as CSV or PDF,
  including learning hours and aggregate exercise feedback.
- **Competition event marks:** optional validated competition logos appear on
  event cards and detail headers.
- **Security baseline:** the v2 interface, data, and delivery process now use
  the OWASP Top 10 as a merge and release requirement. See
  `docs/V2-SECURITY-OWASP-TOP-10.md`.

## Release status

Analytics and reporting are delivered and running on the 24.04 preview host.
2.0 GA remains blocked by the 24.04 network/lab/recovery gates described in
`docs/V2-PROGRAM-CHARTER.md`. Multi-host HA moved to v3 and is not a 2.0 release
gate; see `docs/V3-HA-LAB-POOL.md`.

## Upgrade notes for the development line

1. Take a database snapshot before upgrading.
2. Pull the current `main` commit.
3. Rebuild the backend and frontend images.
4. Start the stack and confirm `/health` and `/api/version` respond.
5. Verify the new `exercise_reactions` table and the `users` login-streak and
   email-consent columns exist.

The backend startup migration is idempotent and creates the new table and
columns automatically. Existing users, courses, completions, and achievements
are preserved.

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
