# Changelog

All notable changes to OpenCyberRange are recorded here.

## Edition model

- **Community / Academic 1.1** — supported single-host teaching platform, lab
  and workbook improvements, exercise authoring, maintenance, and security.
- **Professional 2.0** — Community / Academic plus analytics, reporting, cohort
  analysis, competency evidence, accreditation support, and research exports.
- **Enterprise 3.0** — Professional plus HA, SSO, enterprise reporting,
  multi-tenant support, LMS integration, and compliance reporting. See
  `docs/EDITIONS.md`, `docs/decisions/0002-edition-model.md`, and
  `docs/decisions/0003-edition-scope-refinement.md`.

### Professional and Enterprise priorities

- Competency Framework Engine.
- Student Feedback Engine.
- Radar / Spider Web Reporting.
- Exercise Health Analytics.
- Instructor Intervention Dashboard.

These five priorities are Professional 2.0 and Enterprise 3.0 only. See
`docs/PROFESSIONAL-PRIORITIES.md` and `docs/PROGRAMME-REPORTS.md`.

## [2.1.2] - 2026-11-05

Maintenance release for the Professional line.

### Admin user management
- The Users table shows the last sign-in time, with a relative label and the
  exact timestamp on hover.
- Added filters for status, role, last sign-in window, and VPN registration,
  plus a sort control, result range, clear-filters action, and empty state.
- Role and account status are separate columns; the table has accessible
  headers and a stacked layout on narrow screens.

### Reliability
- Rate limiting now degrades to in-process limits when Redis is unavailable
  instead of returning HTTP 500 on login.

### Design and release
- Added the OpenCyberRange Design Tester skill for light/dark, layout, filter,
  and accessibility reviews.

## [2.1.0] - 2026-11-04

### Login experience
- The login preview shows a sample learner certificate and SWOCTS branding, with
  links to the SWOCTS website and LinkedIn page.
- The exercise like/dislike control now sits at the top of the active exercise
  instead of below the scenario and flag form.

### Admin experience
- The admin user record preview now has an account hero, learning summary,
  searchable completion evidence, active-session cards, and a clear separation
  between read-only review and destructive resets.
- The edit-user dialog now groups identity, access, and password recovery, with
  keyboard-visible focus, inline help, and mobile layouts.
- Admin password reset is a separate privileged action: the admin must
  re-authenticate, the target's sessions are revoked, a password change is
  forced, and the action is audited. The general profile update endpoint now
  rejects password changes.

### Learning and career guidance
- Each track now shows a certification pathway panel with entry, core, and
  advanced vendor certifications, role direction, and links to the Security
  Certification Roadmap, the CISO MindMap 2026, and SWOCTS resources.
- The community/academic backlog records the CISO MindMap-informed curriculum
  breadth and the in-workspace exercise brief pop-out.

### Security
- Serve a deny-all `robots.txt`, send `noindex`/`nofollow` metadata and
  `X-Robots-Tag`, and return `403` to known search and AI crawler user agents.
- Preserve an upstream `X-Forwarded-Proto` so certificate and mail links keep
  the public HTTPS scheme behind a TLS-terminating proxy.
- Document Nginx Proxy Manager WebSocket, SSE, upload, forwarded-header, and
  crawler settings in `docs/REVERSE-PROXY.md`.

### 2.x feature scope
- Reporting, learning analytics, cohort analysis, competency evidence, and
  survey insight are the active Professional feature workstreams. The five
  Professional priorities are defined in `docs/PROFESSIONAL-PRIORITIES.md`.
  Multi-host HA, SSO, multi-tenancy, LMS integration, and compliance reporting
  are Enterprise 3.0; see `docs/V2-PROGRAM-CHARTER.md`,
  `docs/V3-PARKING-LOT.md`, and `docs/V3-HA-LAB-POOL.md`.
- The OWASP Top 10 is the 2.x security baseline for the interface, data, and
  delivery process, with required tests and a documented exception process. See
  `docs/V2-SECURITY-OWASP-TOP-10.md`.

### 2.x analytics and reporting
- Learning hours: tracked time on completed exercises, with bounded session
  time for started exercises that have no completion, shown in student and
  course analytics and in the cross-course report.
- Per-exercise like/dislike feedback for learners, aggregated as likes,
  dislikes, and positive rate in course analytics and reports. Learner identities
  are not shown in the aggregate views.
- Global achievements for learning hours (1, 5, 15, and 30 hours) and sign-in
  streaks (3, 7, and 30 consecutive days).
- Cross-course report PDF export, alongside the existing CSV export.
- Optional competition event marks, validated and stored with the same image
  safety rules as sponsor logos.
- Login now records a UTC calendar-day streak without changing the
  authentication decision path.

### Carried forward from 1.1
- SMTP settings in Admin → Settings → Email, including a save-then-test flow.
- Registration email for new accounts, with separate approved and pending-approval messages. The registration form exposes it as an opt-in checkbox with transactional-email privacy language.
- Profile email preferences in Privacy and data, with PIPEDA consent withdrawal language and an auditable consent version/timestamp.

### Maintenance and fixes
- Exercise catalogue and exercise panel responsive pass: visible Completed,
  In progress, Next up, and Locked labels; a retry state when a track fails to
  load; a real keyboard toggle for level headers instead of nested buttons;
  mobile-safe action rows and active-lab headers; and reduced-motion support.
- Fresh installs now include the Redis rate-limit service, and existing
  deployments receive a Redis override during update.
- Public `GET /api/version` and a footer build-version label.
- Certificate verification now rejects non-ASCII digits, emoji, kanji, whitespace, and malformed IDs before any database lookup.
- Documentation now records the Ubuntu 22.04 baseline for 1.1, the Ubuntu 24.04 target for 2.0, the v3 multi-host lab pool plan, and the 2.x program charter.

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
