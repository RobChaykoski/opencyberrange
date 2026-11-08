# SWOCTS Cyber Range 2.4.1

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** - Community / Academic profile plus analytics,
reporting, cohort analysis, competency evidence, accreditation support, and
research exports.
Status: patch release. The 2.4.0 release contains the feature set; 2.4.1
contains the security and UX remediation.

> **Tag note:** the legacy history already contains published `v2.2.0` through
> `v2.3.2` tags. This release uses `v2.4.1` so no existing tag is moved.

Enterprise preview is the separate HA, SSO, enterprise reporting, multi-tenant,
LMS, and compliance-reporting edition. See `docs/EDITIONS.md`.

## Remediation in 2.4.1

- Rejected placeholder `JWT_SECRET` and `SETUP_TOKEN` values at startup.
- Delivered CSP, HSTS, frame, MIME, referrer, permissions, and robots headers on
  the SPA document and deep-link fallback.
- Made host isolation fail closed and aligned the installer with the production
  Compose stack and systemd project name.
- Added the desktop-recommended notice to exercise-attached RangeBox, a Close
  action, `100dvh`, and safe-area padding.
- Added the mobile drawer focus trap, skip link, contrast-safe navigation
  tokens, and a guest theme control.
- Moved RangeBoxHome onto the shared palette and added a stop confirmation.
- Fixed the zero-evidence career recommendation, added CPU/disk capacity gates,
  and removed scope tokens from logs.
- Refreshed manual screenshots, sizing guidance, VPN guidance, workbook index,
  and architecture diagrams.
- Added CI regression checks for placeholder secrets, SPA security headers,
  local documentation assets, and RangeBox spawn-lock serialization, plus an
  optional deployment UI smoke workflow.
- Added a sticky Briefing / Targets / Flag / Hints jump bar to the mobile
  Active Lab and generated workbook coverage from lab metadata.
- Configured the scheduled UI smoke workflow against the public production URL
  with a dedicated smoke account.

## Highlights in 2.4.0

- **Mobile student shell:** phone-width detection, a compact top bar, an
  off-canvas navigation drawer, and a five-tab student bottom bar (Home,
  Exercises, RangeBox, Courses, Profile).
- **RangeBox workspace:** the standalone launcher and viewer now live in their
  own sidebar tab. The dashboard card was removed, and the tab shows the live
  deployed count.
- **RangeBox reliability:** the deployed meter counts boxes from creation, waits
  for the VNC port before reporting ready, retries the first desktop connection,
  and prevents concurrent launches from overshooting the capacity.
- **Events:** the user-facing Competitions area is now **Events**, with canonical
  `/events` routes and compatibility redirects.
- **Learner profile:** five focused tabs, a visual skill tree, practice
  affinities, and career-profile dossiers with Markdown and printable HTML.
- **Admin navigation:** **Monitoring** is now **Live activity**, covering
  Sessions, VPN Peers, and the Activity Log.
- **Accessibility and text:** repaired double-encoded UTF-8 in profile and admin
  text, including the avatar-border label and profile em dashes.
- **Dependencies:** safe patch updates to FastAPI, SQLAlchemy, Pydantic, and
  psycopg, plus `websocket-client` for the RangeBox load test. Frontend majors
  moved to Vue Router 5.4.0 and ESLint 10.14.0 with `eslint-plugin-vue` 10.12.0.

## RangeBox capacity guidance

Measured results and recommended class limits are in
`docs/RANGEBOX-CAPACITY.md`. The memory-derived maximum is an upper bound; VNC
responsiveness and CPU contention arrive first. A 12 vCPU / 62 GiB host is
comfortable at 20 concurrent boxes, and an 8 vCPU / 30 GiB host at about 8.

## Upgrade notes

1. Take a database snapshot before upgrading.
2. Pull the current `main` commit or the `v2.4.1` tag.
3. Rebuild the backend and frontend images.
4. Start the stack and confirm `/health` and `/api/version` report `2.4.1`.
5. Confirm the RangeBox tab shows the deployed count and that an existing lab
   still launches.
6. Rebuild the workbook wiki and user manual after pulling the documentation.
7. On a host that offers Kali RangeBoxes, confirm
   `docker images opencyberrange/rangebox:lite` is present.

The backend startup migration is idempotent. Existing users, courses, sessions,
completions, achievements, and backups are preserved.

## Verification

- Backend test suite: 193 passed, 5 skipped.
- Frontend lint and production build pass.
- Documentation link check: 310 Markdown files, no broken links.
- Development UI: 101 checks, 0 failed.
- Development mobile shell: 15 checks, 0 failed.
- Production desktop: 25 checks, 0 failed.
- Production admin mobile shell: 12 checks, 0 failed.
- Production Kali RangeBox: launched, reported ready, VNC connected, and was
  destroyed cleanly.
- Database restore drill: restored into a temporary database; 35 users,
  148 labs, and 1,107 activity events verified, then the temporary database was
  removed.
- Production reboot drill: `ocr-platform.service` returned active; all four
  containers were healthy; the deployment reported 2.4.1 after the reboot.
- GitHub CI on both repositories is green.
- GitHub release: <https://github.com/RobChaykoski/opencyberrange/releases/tag/v2.4.1>

## Known limitations

- The embedded RangeBox desktop is replaced on phones with a desktop-recommended
  notice and an optional full-screen link. A laptop is the better choice for
  hands-on lab work.
- Instructor and admin operational screens are reachable on a phone but are not
  optimised for one.
- The production `ocr-platform.service` unit still needs a host-side project-name
  correction; the Compose stack itself is healthy.

# SWOCTS Cyber Range 1.0.0 (powered by OpenCyberRange)

Released: 4 November 2026

SWOCTS Cyber Range 1.0 is the first supported self-hosted teaching release, powered by OpenCyberRange. It is intended for instructors and platform administrators running hands-on cybersecurity exercises on their own infrastructure.

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
