# OpenCyberRange Community / Academic 1.1.2

Edition: **Community / Academic** — supported single-host teaching platform,
lab and workbook improvements, exercise authoring, maintenance, and security.
Professional 2.1 adds analytics, reporting, cohort analysis, competency
evidence, accreditation support, and research exports. Enterprise 3.0 adds HA,
SSO, enterprise reporting, multi-tenant support, LMS integration, and
compliance reporting.

Released: 5 November 2026

OpenCyberRange 1.1.2 is a maintenance release for Ubuntu 22.04 LTS and Ubuntu
24.04 LTS. It keeps the 1.1 deployment and upgrade path.

## Highlights

### Admin user management

- The Users table now shows the **last sign-in** time. The cell uses a readable
  relative label and exposes the exact local timestamp on hover.
- New filters for **status**, **role**, **last sign-in window** (today, 7 days,
  30 days, or never), and **VPN registration**, plus a sort control.
- A result range, a clear-filters action, and a real empty state replace the old
  single-line count.
- **Role** and **account status** are separate columns instead of one badge that
  mixed them together.
- The table uses accessible column headers and switches to stacked rows on
  narrow screens.
- The user detail view now shows the account name and last sign-in.

### Reliability

- Rate limiting now degrades to in-process limits when Redis is unavailable.
  A Redis outage no longer turns login into HTTP 500.
- Added regression coverage for the limiter configuration and the admin user
  API contract.

### Design and release

- Added the **OpenCyberRange Design Tester** skill. It reviews a design change
  against the design skill for view hierarchy, light and dark themes, responsive
  layout, filters, table density, and accessibility.
- Release version is now **1.1.2** in `GET /api/version`, the footer, and the
  frontend package.

## Upgrade notes

1. Take a database snapshot.
2. Pull the `v1.1.2` tag or the matching release commit.
3. Rebuild the backend and frontend images.
4. Start the stack and verify `GET /api/version` reports `1.1.2`.
5. Open **Admin → Users** and confirm the last sign-in column and filters.

## Supported scope

- Ubuntu 22.04 LTS and Ubuntu 24.04 LTS for the 1.x maintenance line.
- Self-hosted Docker Compose deployments.
- WireGuard learner access, with optional WSTunnel deployments.

## Known limitations

- SMTP delivery is best effort. A failed relay never blocks account creation.
- The SMTP password is stored in `platform_settings` and masked in the admin API,
  not encrypted separately. Protect database backups.
- Last sign-in is recorded on successful login. Accounts that have never signed
  in show `Never`.

## Previous release

See the `v1.1.1` tag for the 1.1.1 release notes.
