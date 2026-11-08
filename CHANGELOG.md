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

## [Unreleased]

No changes yet.

## [2.4.1] - 2026-11-08

### Review remediation
- Rejected placeholder `JWT_SECRET` and `SETUP_TOKEN` values at startup.
- Added a shared security-headers snippet to the SPA entry point and deep-link
  fallback, including CSP, HSTS, frame, MIME, referrer, permissions, and robots
  controls.
- Made the installer copy the checked-in production Compose stack, aligned the
  systemd project name, and raised the start timeout.
- Made host isolation fail closed when firewall rules cannot be verified.
- Added the mobile notice/opt-in to exercise-attached RangeBox, a Close action,
  `100dvh`, and safe-area padding.
- Added a mobile drawer focus trap, skip link, contrast-safe navigation tokens,
  and a guest theme control.
- Moved RangeBoxHome onto the shared token palette and added a stop confirmation.
- Fixed the zero-evidence career recommendation and added evidence counts to
  practice affinities.
- Added CPU and disk headroom to RangeBox admission.
- Removed scope tokens from logs.
- Refreshed manual screenshots, publication labels, sizing guidance, VPN key
  guidance, and the architecture diagrams.
- Added CI regression checks for placeholder secrets, SPA security headers,
  local documentation assets, and RangeBox spawn-lock serialization, plus an
  optional deployment UI smoke workflow.
- Added a sticky Briefing / Targets / Flag / Hints jump bar to the mobile
  Active Lab.
- Added generated `Workbook/COVERAGE.md` from lab metadata and a CI check that
  it stays current.
- Configured the scheduled UI smoke workflow against the public production URL
  with a dedicated smoke account.

### Patch release
- This patch follows the 2.4.0 feature release and contains the security, mobile, capacity, and documentation remediation above.
- Verified a database restore into a temporary database and a production reboot
  with `ocr-platform.service` active and all containers healthy.

## [2.4.0] - 2026-11-08

> **Tag note:** the legacy history already contains published `v2.2.0` through
> `v2.3.2` tags. This release uses `v2.4.0` so no existing tag is moved.

### Branding
- Rebranded the user-facing platform as **SWOCTS Cyber Range** with the SWOCTS
  crest as the primary mark and title.
- Added **Powered by OpenCyberRange** attribution with the OpenCyberRange shield
  across the sidebar, login, footer, certificates, emails, PDF reports, and
  documentation.
- Updated MkDocs site names, logos, favicons, and copyright lines, plus the
  frontend title, favicon, and meta description.
- Kept internal package names, API paths, data formats, environment variables,
  and upstream attribution unchanged for compatibility and licensing.

### Learner profile and career discovery
- Split the profile into five focused tabs: **Overview**, **Skill tree**,
  **Learning record**, **Account**, and **Security & privacy**. The selected tab
  is kept in the URL.
- Added a visual **skill tree** to the Skill tree tab, built from the five Cyber
  DNA trait scores, with branch scores, evidence cards, and next steps.
- Added **Practice affinities** to Cyber DNA: positive, evidence-based role
  families for Offensive Security / Penetration Testing, Defensive Security /
  SOC, DFIR / Investigation, and Security Leadership / Education.
- An offensive-security affinity is recognised from completed web, exploitation,
  privilege-escalation, post-exploitation, and credential-attack labs, with
  supporting reconnaissance and enumeration evidence. It is framed as practice,
  not a job label, certification, or testing authorisation.
- Added development-only **career discovery profiles** and a dossier exporter.
  `seed_career_profiles.py` creates a well-versed learner, a starting learner,
  and a career-changer, then exports JSON, Markdown, and printable HTML with
  Cyber DNA, learning evidence, reflection questions, and external resources.
- Added external references for MalOps, Hack The Box Academy, PacketLabs,
  Cisco Networking Academy, and LabShock for IoT/OT training. Links are
  references only; third-party content is not copied or reproduced.

### Admin navigation
- Renamed the admin **Monitoring** tab to **Live activity** in the sidebar and
  panel heading. The tab still holds Sessions, VPN Peers, and the Activity Log,
  and `/admin?tab=monitoring` and the legacy sub-tab links are unchanged.

### RangeBox
- Moved the standalone RangeBox launcher and viewer from the student dashboard
  to its own **RangeBox** tab in the sidebar.
- The tab shows the number of deployed boxes and refreshes it immediately after
  launch or stop. A box is counted from container creation, so the meter does
  not briefly read zero while the desktop is starting.
- RangeBox status now waits for the VNC port before reporting ready, and the
  desktop retries the first connection if websockify is still starting.
- Added `websocket-client` to the backend requirements so the Level 4 RangeBox
  stress test can run, and made its pre-spawn and VNC connect steps wait for the
  desktop to accept connections.

### Mobile student shell
- Added automatic phone-width detection and a dedicated mobile shell: a compact
  top bar, an off-canvas navigation drawer, and a bottom tab bar for Home,
  Exercises, RangeBox, Courses, and Profile.
- The drawer closes on navigation, the backdrop, or Escape, and the mobile shell
  keeps page-level horizontal overflow at zero.
- The embedded RangeBox viewer is replaced on phones with a desktop-recommended
  notice and an explicit full-screen opt-in.

### Events rename
- Renamed the user-facing **Competitions** area to **Events** across the
  sidebar, list, detail, registration, profile, and manuals.
- Added canonical `/events` and `/events/:id` routes. The existing
  `/competitions` routes redirect for older bookmarks, and the API/model names
  remain unchanged for data compatibility.

### Version policy
- Adopted **one platform release number** for this tree on 2.1.4; 2.4.0 continues the same policy. Community /
  Academic, Professional, and Enterprise are edition profiles, not three
  separate version lines. See `docs/decisions/0004-single-platform-release-version.md`.
- Kept Community / Academic 1.1.3 as the supported maintenance line for existing
  single-host installs.
- Described Enterprise as a **preview profile on the current release** until the HA workstream
  ships; the separate HA repository has its own version and compatibility
  statement.

### Course workspace and feedback
- Redesigned the Academy course page around **Overview**, **Content**,
  **Feedback**, and **Achievements**. The public scoreboard is no longer
  presented; scoring data remains available to private reports.
- Added a private two-way feedback loop: students use the existing survey engine
  for a one-minute course check-in, instructors add coaching notes, and the
  summary aggregates check-ins, exercise pulse surveys, reactions, and
  coaching. Existing pulse data feeds the metrics on first load.
- Added optional exercise knowledge checks: 2–3 randomised questions per
  attempt, unlimited re-attempts, explanations and primary references, four
  benchmark achievements, and Cyber DNA evidence. Ten certification-aligned
  lab banks plus track fallbacks cover every exercise. Post-quiz ratings feed
  course satisfaction, relevance, usefulness, and ease-of-use metrics.
- Added an EXIF metadata investigation lab with a safe evidence image, GPS,
  device, author, and free-text metadata, plus a full beginner workbook.

### Host OS validation
- Certified Ubuntu 24.04 LTS for 2.4.1 after WireGuard, firewall persistence,
  KVM, restore, and the full lab matrix passed on 24.04.5.
- Fixed VPN forwarding on hosts where Docker's per-network `DOCKER-FORWARD`
  drops shadowed the `FORWARD` ACCEPT rules. The accepts now live at the top of
  `DOCKER-USER`, and duplicate copies from concurrent startup workers collapse.
- Allowed the Docker bridge pool to reach the Peer Manager on TCP/5000 so the
  backend can re-apply VPN rules on UFW-enabled hosts after a reboot.
- Added the missing `ocr-network-tap` build context and wired it into the
  installer. Capture labs no longer spawn without a tap, and the tap and GRETAP
  mirrors share one TC filter so both receive traffic.

### Dependencies and maintenance
- Applied safe patch updates within declared ranges: FastAPI 0.162.2,
  SQLAlchemy 2.1.8, Pydantic 2.14.3, psycopg 3.3.8, Vue 3.5.45, Chart.js 4.6.1,
  marked 18.1.3, Vite 8.3.6, and globals 17.14.0.
- Confirmed `npm audit` reports 0 vulnerabilities and `pip-audit` reports no known
  vulnerabilities. Upgraded the frontend majors: Vue Router 5.4.0, ESLint
  10.14.0, `@eslint/js` 10.0.1, `eslint-plugin-vue` 10.12.0, and
  `vue-eslint-parser` 10.4.2.
- Reconciled `versions.yaml` and `docs/SUPPORTED-VERSIONS.md` with the installed
  backend and frontend dependency set.

### CI and security scanning
- CodeQL skips analysis on private development mirrors, where code scanning is
  unavailable without GitHub Advanced Security. The public canonical repository
  continues to run it.
- Trivy always runs and uploads a SARIF artifact, but uploads to code scanning
  only where that feature is enabled.
- Removed new CodeQL findings from the career-profile seed and test fixtures.

### Reliability
- Fixed the instructor and admin dashboard Pulse chart on PostgreSQL. The
  `date_trunc` bucket expression is now identical in `SELECT` and `GROUP BY`,
  so PostgreSQL no longer raises a grouping error for `/api/dashboard/instructor/pulse`.
- Repaired double-encoded UTF-8 in user-facing text. The profile avatar-border
  label now shows `Solid · Blue` instead of `Solid Â· Blue`, and dashes,
  ellipses, multiplication signs, and bullets render correctly across the
  profile and admin views.

### Operations
- Added `scripts/status-dashboard.py`, a small API-based dev/prod status
  dashboard. It checks `/api/version`, `/api/setup/status`, and the SPA index,
  writes HTML/Markdown/JSON snapshots, and never logs in or reads learner data.
- Added generated deployment status snapshots under `docs/`.

### Reporting and navigation
- Restored **Reports & analytics** to the sidebar after the link was dropped in
  the Skill DNA navigation change. Administrators see it in the **Admin**
  section; instructors see it in the **Instructor** section. It opens `/reports`
  as a separate route, so the Admin tab is preserved.
- Restored the **Surveys** link for instructors and administrators. Both routes
  existed but had no visible navigation entry.
- Updated the admin guide, navigation guide, instructor report guide, README,
  and analytics documentation for the reporting entry point.
- Added reusable screen-reader-only styles and a caption for the reports table,
  so visually hidden labels stay hidden and table structure is announced by
  assistive technology.
- Report export audit records now include the export scope, and PDF exports also
  record the course count.

### Administration
- Added **Admin → Users → Import / Export Users**: portable user JSON export,
  preview-before-import, optional update of matching usernames, and optional
  avatar export.
- User imports now never overwrite an existing administrator. The signed-in
  administrator is protected by user ID and other administrators are skipped
  with a warning.
- Added **Admin → System → Backups → Restore from another system**: upload a
  plain `.sql` snapshot and restore it or stage it as a local snapshot. Uploads
  are administrator-only, extension-checked, and capped at 512 MB.

### Privacy and security
- Every data export now requires a reason of at least five characters. The
  reason, exporter, format, and scope are written to the audit log.
- Applied the reason requirement to user, activity-log, backup-download,
  learning-report, course/student/assignment-report, and exercise/stress-test
  exports. Self-service account and transcript exports record fixed purposes.
- Export responses use `Cache-Control: no-store`; administrative user exports
  embed `reason` and `exported_by` in the JSON.
- Added `docs/PRIVACY-AND-DATA-DELETION.md`, `SECURITY.md`, OWASP evidence, and
  admin-guide coverage for user migration, cross-system restore, and export
  accountability.

## [2.1.4] - 2026-11-05

### Reporting
- Added the **skill tree radar** to Learning reports. The chart maps assigned and
  completed exercises across the five Skill DNA branches: Explorer, Builder,
  Defender, Investigator, and Leader.
- Added an **All courses** view plus a per-course scope selector, with an
  accessible table fallback beside the chart.
- Extended CSV export with per-course skill-tree mixes and added a skill-tree
  coverage table to the PDF export.
- The reporting API now returns a `skill_tree` object on each course row and in
  report totals.

### Notes
- The radar describes the **mix of exercises**, not learner scores. Completed
  exercises are distinct exercises with at least one completion.
- Learner-level and cohort competency radar remain planned.

## [2.1.3] - 2026-11-05

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
