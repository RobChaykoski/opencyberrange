# Changelog

All notable changes to OpenCyberRange are recorded here.

## [Unreleased]

### 2.x feature scope
- Reporting, learning analytics, survey insight, and the HA lab pool remain the
  only active feature workstreams. See `docs/V2-PROGRAM-CHARTER.md`.

### Carried forward from 1.1
- SMTP settings in Admin → Settings → Email, including a save-then-test flow.
- Registration email for new accounts, with separate approved and pending-approval messages.

### Maintenance and fixes
- Fresh installs now include the Redis rate-limit service, and existing
  deployments receive a Redis override during update.
- Public `GET /api/version` and a footer build-version label.
- Certificate verification now rejects non-ASCII digits, emoji, kanji, whitespace, and malformed IDs before any database lookup.
- Documentation now records the Ubuntu 22.04 baseline for 1.1, the Ubuntu 24.04 target for 2.0, the multi-host lab pool plan, and the 2.x program charter.

## [1.0.0] - 2026-11-04

First supported self-hosted teaching release.

### Learning and recognition
- Certificates with selectable designs, verification links, QR codes, and SWOCTS trust marks.
- Certificate achievements are scoped to the certificate's level, course, or related competition.
- Profile course-achievement summaries grouped by course, with competition and range-wide badges separated.
- Celebration Wall avatars, profile photos, and configurable avatar border styles and colours.
- Competition-specific achievements, including participation, first blood, clean sweep, perfect event, and placements.
- Multi-sponsor competitions with Gold, Silver, and Bronze tiers, descriptions, website links, and uploaded logos.

### Teaching and administration
- Course enrollment, invite codes, scoreboards, achievements, and PDF reports.
- Exercise completion matrix redesigned as a course-by-level progress view.
- Activity-log export and audited clearing.
- User transfer, account erasure, suppression-ledger support, and personal-data export timestamps.
- Persistent database snapshots with daily automatic collection and 30-day retention.
- Snapshot heatmap now reflects actual snapshot files rather than audit events.

### Security and accessibility
- Unicode-aware password policy with control-character rejection.
- Server-side avatar and sponsor-logo validation with size and dimension limits.
- NFKC-normalised, case-insensitive course invite-code lookup.
- Accessibility improvements across progress bars, password controls, admin selects, and track rows.
- Onboarding tour shown once per user rather than on every login.

### Fixed
- Profile summary JSON serialization failure for certificate achievements.
- Celebration Wall avatars missing from the public payload.
- Personal-data panel permanently showing "Checking your last download…" with no prior export.
- Snapshots disappearing after backend container recreation.
- Certificate achievements leaking awards from unrelated exercises, courses, or events.

## [Pre-1.0]

Earlier development builds established the lab catalogue, WireGuard access, Docker lab orchestration, curriculum, authentication, MFA, privacy tooling, and deployment automation. They are superseded by 1.0.0.
