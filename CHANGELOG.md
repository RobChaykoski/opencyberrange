# Changelog

All notable changes to OpenCyberRange are recorded here.


### Branding
- Rebranded the user-facing platform as **SWOCTS Cyber Range** with the SWOCTS crest as the primary mark and title.
- Kept **OpenCyberRange** as the powered-by attribution with the OpenCyberRange shield.

## [1.1.3] - 2026-11-05

### Learner profile
- Added **Skill DNA**: five activity-based traits (Explorer, Builder, Defender,
  Investigator, Leader), a class, a tier, and a certification alignment card on
  the profile.
- Added achievement **titles**. Unlocked titles can be equipped or cleared; the
  class title returns when no achievement title is equipped. Hidden titles stay
  secret until unlocked.
- Added the **Title collection** and the equipped-title badge on the profile.
- Added explicit course, competition, advanced-lab, and teaching signals to the
  Leader trait.
- Added the metric model in `docs/SKILL-DNA.md`.

## [1.1.2] - 2026-11-05

Maintenance release for the Community / Academic line.

### Admin user management
- The Users table shows the last sign-in time, with a relative label and the
  exact timestamp on hover.
- Added filters for status, role, last sign-in window, and VPN registration,
  plus a sort control, result range, clear-filters action, and empty state.
- Role and account status are separate columns; the table has accessible
  headers and a stacked layout on narrow screens.
- The user detail view shows the account name and last sign-in.

### Reliability
- Rate limiting now degrades to in-process limits when Redis is unavailable
  instead of returning HTTP 500 on login.

### Design and release
- Added the OpenCyberRange Design Tester skill for light/dark, layout, filter,
  and accessibility reviews.

## [1.1.1] - 2026-11-04

Maintenance release for the Community / Academic line.

### Security and operations
- Deny-all `robots.txt`, `noindex` metadata, `X-Robots-Tag`, and a crawler
  user-agent block for search and AI scrapers.
- Preserve an upstream `X-Forwarded-Proto` so certificate and mail links keep
  the public HTTPS scheme behind a reverse proxy.
- Admin password resets now require the administrator's own password, revoke
  the target's sessions, force a password change, and are audited. The general
  profile update endpoint rejects password changes.
- Nginx Proxy Manager guidance for WebSockets, SSE, uploads, forwarded headers,
  and crawler blocking.

### Learning and guidance
- Login preview certificate and SWOCTS branding with website and LinkedIn links.
- Certification pathway panel on each track, with links to the Security
  Certification Roadmap, the CISO MindMap 2026, and SWOCTS resources.
- Community / Academic edition naming and scope.

## [1.1.0] - 2026-11-04

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
