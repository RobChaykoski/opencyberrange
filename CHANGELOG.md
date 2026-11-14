# Changelog

All notable changes to OpenCyberRange are recorded here.

## [5.10.0] - 2026-11-14

### Open Badges
- The profile now lists issued Open Badges with status, issue date, name-sharing
  state, viewer links, copy-link, and a toggle to include or omit the display
  name on the public credential. Name-sharing changes are audited, and a
  revoked credential cannot be changed.
- Changing the issuer URL after credentials exist now requires explicit
  confirmation; older credentials keep their original issuer and status URL.
  The issuer form stays disabled until the current settings load.

## [5.9.1] - 2026-11-14

### Open Badges
- The admin Open Badges panel can revoke an active credential with a reason; the
  action is audited and the list refreshes to show the new status.

## [5.9.0] - 2026-11-14

### Open Badges
- Added an admin **Open Badges** settings panel: issuer name and URL, current
  key ID, signing-key count, credential count, recent credentials, and key
  rotation.
- Key rotation publishes the old public key in the JWKS so credentials signed
  before rotation still verify.
- Added a public `/badges/:jti` credential viewer: achievement, issuer, status,
  recipient (or pseudonymous subject), JWKS link, JWT copy/download, and raw
  claims. The certificate page now links to the viewer.
- Added admin-only badge settings/list/rotate endpoints; changes are audited.

## [5.8.1] - 2026-11-14

### Fixes
- Badge eligibility now evaluates only the labs in the requested level, not every
  lab in the track. The first build incorrectly required all track labs before
  issuing a level credential.

## [5.8.0] - 2026-11-14

### Open Badges 3.0
- Hosted **JWT-VC** credentials for completed level certificates, signed with
  Ed25519. The issuer key is generated on first use and stored encrypted; the
  public issuer profile and JWKS are published.
- Learners issue a badge from the certificate page, see the credential link, and
  can copy it. Sharing is opt-in; the credential subject is pseudonymous by
  default, with an optional display name.
- Credentials expose a status endpoint and an audited admin revocation path.
  Migration `0029_open_badges`.
- Phase 1 covers level certificates; event awards, badge images, and third-party
  viewer compatibility testing remain follow-ups.

## [5.7.0] - 2026-11-14

### About
- Added real host package/reboot status. `scripts/collect-host-health.sh` records
  the OS, kernel, uptime, upgradable/security package counts, reboot-required
  flag, and disk free space into the backend's backup volume; About reads it and
  adds an **OS packages** maintenance row and a checked-at summary.
- The collector runs at boot and every six hours from the deploy user's crontab;
  it needs no root and no new mounts.
- Added a **Platform maintenance** browser pass across Admin groups, System
  metrics, About, the instructor overview, and Exercise plan in dark and light
  themes; no console errors.

## [5.6.0] - 2026-11-14

### Cohort enforcement
- Labs in an exercise set required for a learner's cohort now count as course
  access and open without the sequential-track prerequisite lock. The course
  detail listing includes those labs. Cohort-specific access is additive; it does
  not remove anything assigned course-wide.

### Instructor reporting
- The instructor Overview can filter to one student inside a selected course.
  Cards and trends then reflect that learner only; cross-course student filtering
  is intentionally not offered.

### About
- The About page has a **Platform maintenance** section: live host OS, kernel,
  Docker, Python, PostgreSQL, schema, and build toolchain versions with supported/
  target status and the upgrade path. It also shows the operator upgrade and
  rollback commands and the readiness/runbook references.

## [5.5.0] - 2026-11-14

### Course planning
- Added cohorts, exercise sets, and requirements to a course, with migration
  `0028_course_planning`.
- Instructor course workspace has an **Exercise plan** tab: create cohorts and
  pick members from the enrolled roster, build exercise sets from the course
  labs, attach a completion rule (all / percent / count) with a due date and
  note, and see coverage by cohort.
- Coverage shows learners, met/missing counts, overdue state, and per-learner
  completion for the instructor. Usernames respect privacy mode.
- Requirements are planning and coverage in this phase; platform-wide exercise
  access is unchanged. Enforcement of cohort-specific access is a later change.

## [5.4.0] - 2026-11-14

### Instructor
- Added a cross-course **Overview** to the instructor panel: cards for courses,
  unique learners, active learners, completion, completed pairs, and pending
  reviews; a completion/active-learner trend chart; and a course table.
- Filters: 7/30/90-day windows, custom start/end dates, and a single-course
  filter. Course rates are suppressed below five learners; no learner is ranked
  or named. Existing course management tabs are unchanged.

## [5.3.1] - 2026-11-14

### Navigation
- Admin tabs are grouped into People, Learning, Operations, and Configuration
  instead of one flat row; tab keys and routes are unchanged.
- Workbooks moved into the Academy sidebar section for every role; the admin
  Resources section keeps the user manual.
- Added the Academy/instructor/reporting information-architecture proposal
  (`docs/ACADEMY-INSTRUCTOR-REPORTING-IA.md`), including cohorts, exercise sets,
  requirements, trend metrics, and privacy thresholds.

## [5.3.0] - 2026-11-14

### System view
- Added a **Metrics** sub-tab to Admin → System with CPU load, memory, disk,
  active lab sessions, DB connections, live RangeBoxes, and container/image
  counts. Each card shows the current value and an inline history graph, with
  1-hour, 6-hour, 24-hour, and 7-day windows.
- Metrics are sampled every minute from host load/memory/disk, PostgreSQL, and
  the container runtime, retained for 30 days. Admin-only
  `/api/admin/system/metrics` and a manual "Sample now" action back the view.

## [5.2.2] - 2026-11-14

### Fixes
- The startup lab-egress pass now installs `iptables` in its helper container;
  `alpine:latest` does not include it, so the pass had been failing on both
  hosts while the manually applied rules stayed in place.
- The egress policy is also re-applied at boot and every five minutes from the
  deploy user's crontab on development and production.

## [5.2.1] - 2026-11-14

### Security
- Lab and RangeBox egress is default-deny: the host LAN and published platform
  ports, lab gateways (including SSH), the internet, and link-local metadata are
  blocked. Same-lab ranges, the shared target network, and QEMU guests keep
  working. Host-local services are dropped in a dedicated `OCR-LAB-INPUT` chain.
- The backend reattaches to live RangeBox proxy networks on startup, so a
  redeploy no longer breaks VNC for sessions that stay running.

## [5.2.0] - 2026-11-14

### Audit and impersonation
- Admins can open any user's interaction history; instructors can open it for a
  student enrolled in their course. The report combines activity events with the
  impersonation sessions involving that user, and every view is itself audited.
- Impersonation is now recorded server-side for its full lifetime, with
  **live**, **ended**, and **expired** status. The admin Activity tab shows live
  sessions and accepts a username lookup for the full history.
- `impersonation_sessions` migration `0026`, with start/exit audit detail that
  names the target and session.

### Operations
- Backup transports can now write the encrypted set to an SSH/rsync target, an
  already-mounted NFS directory, an SMB share via curl, an rclone remote, or a
  custom command. Off-host copies are encrypted by default; plaintext requires
  the explicit `BACKUP_ALLOW_PLAINTEXT=1` override.

## [5.1.2] - 2026-11-14

### Operations
- The deployment monitor now supports an `ALERT_COMMAND` hook and writes
  `last-failure.txt`, so failures are actionable without a webhook.
- The backup script can upload the encrypted set to an SMB/NAS target via curl
  (`BACKUP_SMB_URL`, `BACKUP_SMB_NETRC`). The NAS copy remains disabled until a
  service account is provided.

## [5.1.1] - 2026-11-14

### Operations
- Off-host backups are encrypted to the **OCR Offsite Backup** key before
  transfer (dump, erasure ledger, and platform env); the local plaintext dump is
  retained for the weekly restore drill. Verified by decrypting the off-host
  copy and matching the SHA-256.
- `scripts/monitor-deployment.sh` runs every 10 minutes and checks the API
  version, backend health, 8443 workbook origin, containers, disk, local and
  off-host backup age, and certificate expiry. Optional Slack-compatible webhook
  via `~/.ocr-monitor.env`.

### Fixes
- The dev-only LDAP plaintext escape hatch now honors
  `SSO_ALLOW_INSECURE_HTTP`, matching the provider validator. This restores the
  local Dex/OpenLDAP stack without weakening production defaults.

## [5.1.0] - 2026-11-14

### Identity
- Identity provider settings export/import: versioned bundle, fixed dry-run
  first, existing names skipped unless requested, missing secrets force a
  provider disabled, admin-only and audited. Secret values are never exported.
- Removed the unused `meta.module` router branch; modules remain enforced by the
  backend middleware and feature flags.

### Operations
- Production backups now push off-host to `ocr-offsite:/home/ocrv2/backups/prod`
  after the nightly dump; the weekly restore drill is unchanged.

### Next
- Open Badges 3.0 hosted credentials are planned for 5.2; the build plan is in
  `docs/OPEN-BADGES-3.0-SCOPE.md` and nothing is claimed as shipped.

## [5.0.1] - 2026-11-14

Security and compliance patch on top of Release 5.

### Security hardening
- LDAP: referral chasing is disabled, and plaintext `ldap://` requires an
  explicit `allow_plaintext` opt-in; `ldaps://` or StartTLS is the default.
- OIDC: ID-token signing algorithms are restricted to an asymmetric allowlist;
  a provider advertising only `HS*`/`none` fails closed. Nonce comparison is
  constant-time.
- SSO: post-login `return_to` rejects backslash and control-character forms in
  both the backend and the SPA.
- Production: `wiki_frame_ancestor` is set for the real app origins so workbooks
  frame on `https://172.16.16.41`, `https://ctfd.swocts.com`, and the public IP.

### Review record
- Added `docs/SECURITY-REVIEW-5.0.1.md` covering the SSO review, route-guard and
  bundle exposure check, frontend licence scan, and IdP export assessment.

## [5] - 2026-11-14

Release 5. LTI 1.3 Advantage, per-student accommodations, human review, the
tabbed workspace, and the associated procurement evidence. Production and
development both run this release from `main`.

### LTI 1.3 Advantage
- Platform registry, OIDC third-party login (GET and form POST), signed
  `id_token` validation, single-use state, external-identity linking, and the
  SPA ticket exchange.
- AGS 2.0: private_key_jwt token exchange, line items, reviewed score passback,
  result retrieval, and an append-only ledger.
- NRPS 2.0: explicit roster sync with the minimum subject/role/status/context
  fields and LIS 2.0 membership parsing.
- Deep Linking 2.0: single-use picker, signed response, lab launch content
  items, selection limits, and an embeddable picker/callback.
- Public tool JWKS with an RFC 7638 `kid` on every signed message.
- Verified end to end against Moodle 5.0.2, including a grade reaching the
  Moodle gradebook and NRPS returning the course roster.

### Accommodations
- Per-student 1.0x–3.0x timed-session multiplier and 0–365 day due-date
  extension, managed by instructors and audited.
- Learner pause/resume clock with a reason, a frozen expiry, scheduler
  exclusion, and paused-time credit on resume.
- Append-only `accommodation_events` and activity-log records.

### Learning workspace
- The exercise view uses full-size **Desktop**, **Exercise**, and **Workbook**
  tabs instead of a split grid. The desktop stays mounted across tab switches
  so the VNC session is not dropped. The briefing, flag, hints, and workbook
  remain one click away.
- The same tabs appear for every lab. The Desktop tab shows RangeBox, VPN
  connection guidance, a start prompt, or the mobile notice instead of
  changing the whole page layout. The selected lab and tab persist in the URL
  across refresh and back/forward.
- The RangeBox toolbar is the single desktop bar: the duplicate pane header is
  gone, and connection/clipboard/fullscreen/quality controls stay in one place.
  Left/right arrow keys move between tabs.
- Workbooks can be served from a dedicated wiki origin. Dev uses
  `https://172.16.16.44:8443`, so the framed workbook keeps its own storage and
  search without access to the SPA token; the SPA CSP allows that frame.
- The workbook iframe loads only when the Workbook tab is first opened. It
  stays mounted afterwards, so switching tabs does not reload it or lose its
  scroll position.

### Human review
- The exercise result panel states that flag matching is deterministic and
  offers a human-review request. Learners see pending/approved/rejected status
  and the instructor's note.
- Instructors review pending requests per course, approve or reject with a note,
  and every request/decision is audited.

### Minor accounts
- Minor enrollments can record the institution's parental/guardian consent
  reference and the staff member who recorded it. The roster flags missing
  consent, and changes are audited. Identity documents are not stored.
- Each course has a retention date and note. Administrators can preview the
  learner records in scope and record an append-only completion reference after
  the documented backup-and-purge runbook step.

### RangeBox
- Pinned the Kali base image digest and the SecLists commit.
- Baked the wordlists the labs reference at their documented paths: `common.txt`
  (also at `/usr/share/wordlists/dirb/common.txt`), the DirBuster medium list
  (also at `/usr/share/wordlists/dirbuster/`), the DNS top-5000 list, and two
  password shortlists. The upstream medium-list filename moved; the download now
  uses the pinned path that resolves.
- Documented the root-inside-caged-container model and the Firefox content
  sandbox rationale in `RangeBox/SECURITY-MODEL.md`.

### Operations
- Migrations `0015`–`0025`.
- Development `172.16.16.44` tracks `main`; live lab spawn, pause/resume,
  accommodation read-back, 10-lab sampling, and an authenticated page pass all
  verified.
- Production `172.16.16.41` deployed on 2026-11-14: version 5, Alembic
  `0025_review_requests`, 179 labs, backend/frontend healthy, 8443 workbook
  origin responding.

## [4.0.2] - 2026-11-14

Release 4 production hotfix. Frontend only; schema and API remain Release 4.

### RangeBox workspace
- Desktop, Exercise, and Workbook are full-size tabs instead of a split grid.
- RangeBox stays mounted across tab switches.
- The desktop toolbar wraps in narrow panels instead of clipping controls.
- See [`RELEASE-4-HOTFIX-4.0.2.md`](docs/RELEASE-4-HOTFIX-4.0.2.md).

## [4] - 2026-11-12

Release 4. Enterprise single sign-on, the optional Dex/OpenLDAP test stack, and
the privacy, accessibility, and API-exposure corrections.

### Enterprise SSO
- OIDC authorization-code login with PKCE, state, nonce, discovery, JWKS, and
  issuer/audience/signature validation.
- SAML 2.0 SP-initiated login with signed assertion validation and shared
  RelayState/AuthnRequest state.
- LDAP/Active Directory sign-in with a service bind, user rebind, filter
  escaping, StartTLS, and certificate verification.
- One provisioning/linking service for all adapters: verified-email linking,
  administrator-link refusal, SSO-only accounts, and instructor group mapping.
- Directory role mapping is refreshed on every SSO login, so a group change takes
  effect without an administrator editing the account.
- Optional `sso` compose profile with Dex (OIDC) and OpenLDAP, a generated Dex
  config, LDAP bootstrap users, and an `/idp/` nginx proxy for local testing.
- The local administrator password login remains as break-glass access.

### Security
- The backend now trusts `X-Forwarded-For`/`X-Forwarded-Proto` only from
  loopback and private Docker bridges. Per-IP rate limits and audit rows use the
  real client address instead of the nginx container address.
- SSO states and tickets remain single-use, provider-bound, and short-lived.
- The API-docs and module gates read their setting fresh on every request, so an
  administrator disabling either takes effect immediately instead of after the
  settings cache expires.
- nginx returns 404 for `/docs`, `/redoc`, and `/openapi.json` on the public
  origin; API documentation is never served through the learner-facing host.
- SSO callback failures now render curated user messages instead of raw backend
  error details.
- The CI CSP-hash check fails on both missing and stale inline-script hashes;
  the `v-html` exception remains limited to the two reviewed DOMPurify sites.
- Workbook and launch links go through `safeHttpUrl` and open with
  `noopener,noreferrer`.
- Documented the HttpOnly session-cookie migration roadmap, including CSRF,
  refresh/revocation, wiki-gate, and acceptance criteria.

### Privacy
- Subject-access export now includes external identity links and SSO session
  metadata, without the encrypted ID token or provider secrets.
- Account erasure explicitly removes external identities, SSO sessions, and SSO
  tickets and records the counts in the erasure result.
- Added identity-federation data to the privacy and procurement documentation.

### Accessibility
- The institution sign-in panel is a labelled section with a heading, visible
  directory-field labels, per-provider accessible button names, error
  associations, `aria-busy` state, and visible focus styles.
- Cyber DNA and Cyber GPS use one scale (`/99` for DNA), an accessible
  "How this is calculated" disclosure, and a zero-evidence start card instead of
  an empty radar chart. Career GPS labels each family's evidence band.

### Network device topology
- Added `x-ocr-topology` to Compose: nodes, roles, and point-to-point links are
  validated as data, then expanded into per-session `/29` networks with static
  addresses, forwarding, routes, and node environment.
- Added the reviewed `ocr-lab/topology-node` image with `router`, `host`, and
  `service` roles, SSH, a status endpoint, and a flag service.
- Rejected privileged containers, arbitrary images, host networking, bind
  mounts, hostile capabilities, and reserved environment keys.
- Added the routed-path demo lab plus two-router transit, firewall service path,
  and multi-service router labs, with workbook chapters, engine unit tests, and
  image-only topology support in the static validator.
- Added a guided and an independent Forensics variant on the same engine, with a
  decoy service in the independent version, so learners can choose their pace.
- Added YARA fundamentals and a YARA + incident-log triage scenario, and a
  Windows AD fundamentals lab plus an AD-to-SMB credential-reuse scenario.

### Learner experience
- Dashboard and profile now use the same visible-exercise denominator, and the
  dashboard course matrix, course card, course detail, and profile all use the
  same enrolment-aware completion rule. The course-card percentage rounds
  half-up so it matches the course page.
- New learners see an evidence-first profile: five tabs, no Cyber GPS or
  Portfolio tab, no zero-evidence career affinity, and a progress-only Learning
  record with **Show all tracks** for the rest.
- Experienced learners can focus the profile on a course, track, certification,
  or career goal, with course/track/certificate progress lenses and a searchable
  focus list. The career target is promoted to the top of the Portfolio tab.
- The title collection is collapsed by default with an **Unlocked only** filter,
  and achievement badges use the shared SVG icon system instead of emoji.
- Workbook actions and profile status badges use the shared colour tokens.
  Track difficulty chips, VM status dots, and the safe admin/track status
  surfaces use the same tokens; custom-achievement authoring now uses the SVG
  icon picker.

### Documentation
- Added the compliance posture, procurement traceability, accessibility
  statement, automated-scoring statement, HECVAT answer pack, LTI design
  contract, DPA template, and Release 5 scope.
- Release 4 does not claim LTI, multi-tenancy, a per-student accommodation
  engine, a TA role, a signed VPAT, SOC 2, or ISO 27001.

### Fixed
- Event certificates now transliterate characters the built-in PDF fonts
  cannot encode, so an event date with an en dash (or an accented name) no
  longer fails certificate generation.

## [3.1.1] - 2026-11-05

Enterprise SSO adapter release.

### SAML 2.0 sign-in
- SP-initiated SAML login with signed assertion validation, audience/recipient
  checks, and AuthnRequest ID validation through `python3-saml`.
- Shared PostgreSQL state stores the RelayState and AuthnRequest ID, so the ACS
  can run on a different API replica from the login start.
- ACS endpoint at `/api/auth/sso/saml/{id}/acs`; the SP entity ID and ACS URL
  are shown in the provider card.
- Optional signed AuthnRequests with an SP certificate and private key.
- Attribute mapping for email, username, name, and groups, with an optional
  instructor group.

### LDAP and Active Directory sign-in
- Service bind, user search, and a user rebind to verify the password.
- LDAP filter escaping, StartTLS, certificate verification, and a configurable
  server timeout.
- Attribute mapping for email, username, name, and groups, with an optional
  instructor group.
- Direct institution-account form on the login page; failures distinguish bad
  credentials from a directory outage.

### Shared identity policy
- OIDC, SAML, and LDAP now use one provisioning and linking service.
- Verified-email linking, administrator-link refusal, and SSO-only accounts are
  identical across adapters.
- New accounts can be provisioned as student or instructor through group
  mapping. External identities never receive administrator access.
- Provider test actions validate OIDC discovery, LDAP service bind, and SAML
  settings.

### Documentation
- Added `docs/SSO-SAML-LDAP.md`; updated the OIDC guide, ADR 0004, the
  Enterprise manual supplement, editions, and supported versions.

### Limits
- SAML RP-initiated logout/SLO remains local; OIDC logout remains the only
  IdP-initiated logout path.
- A formal SSO security review remains.

## [3.1.0] - 2026-11-05

Enterprise single sign-on release.

### OIDC SSO
- Authorization-code login with PKCE, state, nonce, discovery, JWKS, and
  issuer/audience/signature validation.
- Shared PostgreSQL flow state and one-time SPA exchange tickets. Any API
  replica can complete a callback started on another replica; no sticky
  sessions are required.
- Stable public callback URL derived from `PUBLIC_BASE_URL`.
- Auto-provisioning, auto-approval, verified-email linking, and SSO-only
  accounts. Administrator accounts are never auto-linked.
- A local break-glass administrator remains available.
- Provider test endpoint for OIDC discovery and JWKS reachability.
- The provider card shows the exact redirect URI to register at the IdP.
- Activity and audit events for SSO login, provisioning, and linking.
- RP-initiated logout when the provider advertises an end-session endpoint.
  The ID token is stored encrypted and removed after use.
- New `password_login_disabled` account flag and `external_identities`,
  `sso_login_states`, `sso_login_tickets`, and `sso_sessions` tables.

### Documentation
- Added ADR 0004 (SSO HA contract) and `docs/SSO-OIDC.md`.
- Updated the Enterprise manual supplement and login guide.
- Moved the Enterprise version line to **3.1.x**.

### Limits
- SAML and LDAP login adapters are not part of 3.1.0; their settings remain.
- A formal SSO security review remains.

## [3.0.3] - 2026-11-05

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

## [3.0.2] - 2026-11-05

Maintenance release for the Enterprise line.

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

## [3.0.0] - 2026-11-04

Enterprise release line.

- LDAP, OIDC, and SAML identity-provider settings with encrypted secrets and
  audit logging (settings-only; login federation remains in the Enterprise HA
  workstream).
- Enterprise inherits the Professional 2.1 analytics, reporting, competency,
  feedback, certification guidance, and admin security changes.
- Multi-host HA, gateway failover, multi-tenancy, LMS integration, and
  regulatory reporting remain in the Enterprise programme; see
  `docs/V3-HA-LAB-POOL.md` and `docs/EDITIONS.md`.

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

## [Release 3] - 2026-11-12

### Cyber DNA 2026.14
- Branch and overall scores are capped at **99**, never 100.
- Each branch decays from its own last practice date (99% at 15-30 days, 97%
  at 31-60, 94% at 61-90, 90% after 90) and a new completion in that branch
  restores it.
- The profile reports a **40-hour continuing-education** target over the
  trailing 12 months and a **30-day directional trend** rebuilt from completion
  and quiz timestamps.
- Spider-chart points scale with **evidence strength**: clean, unaided,
  advanced, assessment, and high-scoring quiz work weighs more.
- The public `signals` payload is JSON-safe, so a populated profile no longer
  returns 500 on serialization.

### Cyber GPS signal
- The GPS shows an active or fading practice signal from completions in the last
  30 days. Active domains shimmer; quiet domains fade and appear as **fading
  interest signals** with a prompt to revisit.

### RangeBox and workbook
- The workbook pane hides MkDocs chrome, uses the full width, scrolls
  independently, and grows to 58vh with **Expand**.
- The RangeBox can **pop out** into its own resizable window while the main tab
  keeps the briefing, notes, and workbook.
- noVNC gains a stream-quality selector, Ctrl+Alt+Del, native fullscreen, focus
  on connect, and clearer security/credential failure messages.
- The flag field captures `OCR{...}` from the desktop clipboard, cleans pasted
  text, and offers **Paste**, **Read clipboard**, and **Use as flag**.
- The RangeBox is **text-only**: file drops, file pastes, and drag-out are
  rejected. No files leave or enter the desktop.
- The user manual adds **Navigating your Cyber DNA** with dev screenshots; the
  admin guide adds **Cyber DNA and RangeBox Operations**.

### Community events
- The **Events** tab keeps platform events at the top and adds an **Around the
  area** calendar underneath.
- The calendar combines internal platform events with community events and
  lists upcoming entries, with source links for SWOCTS Hub and Cyber Hive YXU.
- Community events are explicitly outside Cyber DNA, course credit, and platform
  scoring. The user manual adds **Community Events**.

### Tools
- CyberChef 11.5.0 is now a pinned, SHA256-verified static build served from
  the frontend image at `/tools/cyberchef/`. The Tools panel loads it
  same-origin, so it works on isolated ranges and no longer depends on
  `gchq.github.io` or a widened `frame-src` policy. The location carries a
  tailored CSP with the release's inline-script hashes pinned.

### Reliability
- The expired-session cleanup pass now runs in a worker thread. It performs
  synchronous SQLAlchemy and Docker teardown, so running it on the event loop
  could freeze every request in the single-worker deployment (symptom: every
  page stuck on "Loading…", `/health` timing out).
- Startup schema and ledger advisory locks now time out after 30 seconds
  instead of waiting indefinitely, and Alembic no longer disables existing
  loggers, which had hidden all startup output after the migration step.

## [2.7.0] - 2026-11-11

### Learning
- Added `has_quiz` to each track level and show the level **Quiz** button only
  when the level is complete and an active quiz bank exists.
- Seeded the Beginner level quiz banks: 5 questions for Stage 1, 5 for Stage 2,
  4 for Stage 3, and 4 for Stage 4, with a passing score of 70. The seed script
  is `platform/backend/app/scripts/seed_level_quizzes.py`.
- Added `scripts/ui-learning-smoke.mjs`, which compares the rendered Quiz and
  Certificate buttons with the track API for every level.

### Labs and network
- VPN-only sessions now reveal target IP addresses and the hosts-file mapping;
  RangeBox sessions keep addresses hidden unless `show_target_ips` is set.
- Installed and persisted the WireGuard client-pool route
  `10.255.0.0/16 dev wg0` in `scripts/setup-range-server.sh`, with
  `scripts/fix-wireguard-client-route.sh` for existing hosts.
- Lab cleanup now preserves networks owned by a session that is still
  `starting` or `running`, so a stop/relaunch no longer removes the live
  environment.

### Operations
- Added `docs/DEPLOYMENT-RUNBOOK.md` with pull, rebuild, prebuild, quiz-seed,
  and health commands for development and production.
- The status dashboard reads its host map from `docs/status-hosts.json`.
- Added the public verification smoke and event-certificate PDF layout test.

## [2.6.0] - 2026-11-10

### Events and certificates
- Added event certificates for participation, placement (1st, 2nd, 3rd), and
  trophy challenges (First Blood, Clean Sweep, Perfect Event).
- Certificates render the event logo and gold/silver/bronze sponsor marks in the
  app and in the PDF, and use deterministic `OCR-EVT-` IDs with a SHA-256
  digest.
- Added `/api/competitions/{id}/certificates` and
  `/api/competitions/{id}/certificate/{award}?format=json|pdf`; certificates are
  issued only after the event ends to approved, opted-in participants, and
  placement/trophy awards require the matching event achievement.
- Public verification now accepts event IDs and returns event/award metadata
  without scores or account identifiers. The verification form validates both
  track and event ID formats before enabling submission.
- Added certificate links to the competition detail page and an event mode to
  the certificate view. Certificate opt-out also hides the event verification
  URL and QR code.
- Documented the award model, ID format, API, privacy rules, and tests in
  `docs/EVENT-CERTIFICATES.md`.

### Reporting
- Added a decision-led instructor report library: course health brief, exercise
  diagnostics, coaching queue, and the full student record pack.
- Reports carry a report ID, SHA-256 checksum, and HMAC-SHA256 manifest
  signature; PDFs print the ID and CSV files include it.
- Added cohort mean/median solve-time and hint-use baselines, plus an
  engagement signal for unusually fast, hint-free completion. The signal is a
  support prompt, not an AI accusation or ranking.

### Privacy
- Added under-18 reporting privacy. When enabled, the learner is excluded from
  instructor reports, course analytics, coaching queues, public leaderboards,
  and competition scoreboards; their own dashboard still works.
- Added public certificate verification opt-out. When disabled, the public
  verifier returns the generic invalid result and the certificate payload omits
  the verification URL and QR code.
- Added public `/about` for first-time visitors; detailed installation inventory
  moved to `/about/installation`.
- Added `Cache-Control: no-store` to `/api/about` so a stale release version is
  not cached after deployment.

### Labs and tools
- Added CyberChef to the student Tools menu and the active-lab panel.
- Added three entry-level High School Grade 9 CyberChef labs: Base64 decode,
  Caesar shift/ROT13, and a two-layer Base64 + ROT13 message, with workbook
  pages.
- Added three Grade 9 digital-safety labs: read a lookalike link without
  clicking it, identify a disguised file before opening it, and a capstone that
  combines both, with workbook pages.
- Added a Grade 10 email-metadata lab covering envelope and display headers,
  `Received` chains, SPF/DKIM/DMARC results, and custom `X-` headers.
- Added three Grade 10-12 Digital Frontier labs: lost-phone MFA recovery, media
  provenance verification, and a crypto rug-pull investigation, with workbook
  pages, quizzes, badges, titles, certification pathways, and NICE mappings.
- Added the Identity & Access track with three labs: secure authentication and
  session forgery, OAuth/OIDC redirect and token trust, and joiner/mover/leaver
  lifecycle and access review.
- Hardened the shared High School target with a restrictive CSP, `nosniff`,
  `no-referrer`, frame denial, and a permissions policy.
- Added student-tester and inclusive-curriculum reviews at
  `docs/reviews/CYBERCHEF-LABS-REVIEW.md` and
  `docs/reviews/DIGITAL-SAFETY-LABS-REVIEW.md`.

### Integrity and access
- Added an audited review workflow for unattributed integrity-ledger writes.
  Reviews require an administrator, a decision, a note, and confirmation; the
  review is written to the audit log and append-only ledger.
- Serialized startup schema initialization across workers and made the new
  privacy columns idempotent.
- Refreshed the login/registration pages for AODA: skip links, focus
  management, Caps Lock warnings, password-strength text, target sizes, contrast,
  reduced motion, and explicit privacy/under-18 acknowledgment.
- Redesigned the public certificate verification page with clearer trust,
  privacy, and ID-location guidance.

### Operations
- Deployment, curriculum-seed, discovery, and installer scripts now emit ASCII
  status markers so logs render correctly in Windows terminals and CI.
- Shrunk the WireGuard client footprint: the interface address is `/32`, the
  client routes only its own lab `/24`, and the client pool moved to
  `10.255.x.y`. Existing VPN configs must be re-downloaded; a reallocation
  script and route verifier are included.
- Updated Cyber DNA to formula `2026.13`: raw event joins no longer add Leader.
  Event exercises still count as normal labs, and event success badges (first
  blood, clean sweep, perfect event, placement) still count through
  achievements. Event participation certificates are credentials, not Cyber DNA
  signals.
- Recorded the `v2.6.0` release tag as annotated but unsigned; it points at
  `2835303b`, the commit deployed to production and development on
  11 November 2026. The supply-chain lock remains signed by the release key.

### Security
- Strengthened the shared password policy for registration, password changes,
  and admin resets. It now rejects common bases with a number or symbol appended
  (`Password1!`, `P@ssw0rd2026!`), account-specific words (username, email local
  part, first/last name), repeated patterns, and simple sequences. The
  registration and change-password fields mirror the same checks before submit.
- Added password-policy regression tests covering common-password shortcuts,
  context words, repeats, sequences, and strong passphrases.
- RangeBox launch failures now report the actual cause. A missing desktop image
  returns a specific `409` response instead of a generic server error, and the
  launcher disables images that are not installed on the host.
- The orientation tour now stores its "seen" state on the user account as well
  as in browser storage. It no longer reappears after a change of hostname or
  port, cleared site data, or a second tab racing the first.

### Exercise workspace
- Desktop RangeBox exercises now open in a combined workspace: RangeBox
  top-left, scenario/details and the flag panel on the right, and the workbook
  as a framed pane along the bottom. Phones keep the existing stacked panel.
- The workbook pane has an Expand/Restore control and an open-in-new-tab
  fallback; the flag panel stays visible while the details scroll.
- Launching from the exercise panel now honours the lab's desktop image, and a
  lab whose tools list says `rangebox` launches a Kali desktop instead of
  starting VPN-only.
- Fixed lab-attached RangeBox VNC: the proxy network used the Docker gateway
  address (`.1` on a `/30`) for the desktop, so the viewer stayed on
  "Connecting". It now uses a `/29` with the desktop at `.2` and the backend at
  `.3`, and replaces legacy `/30` networks.
- Student-tested on the High School RangeBox First Steps lab: desktop connected,
  workbook loaded, flag completed the exercise, and the mobile view remained
  single-column without horizontal overflow.
- **Open in new tab** now opens the resolved `/rangebox?...` URL in a new tab.
  It previously routed the exercise tab in place, despite the button label.
- The workbook CSP now allows the Material for MkDocs Google Fonts stylesheet
  and font files. The SPA policy stays strict.
- Added `scripts/ui-workspace-regression.mjs`, which walks the workspace as a
  dedicated test student and test instructor, exercises Expand/Restore, both
  new-tab controls, hint request, invalid-flag handling, and Stop, and records
  JSON evidence plus screenshots. Final run: **44/44 checks passed**.
- Fixed a stop/relaunch race: background cleanup for an old session could remove
  the network and RangeBox created by a newer session for the same lab, which
  silently launched the new lab VPN-only. Cleanup now defers to a newer
  starting/running session and only marks the old row stopped.

### Curriculum and documentation
- Reorganized **WEB01 Web Reconnaissance** into a 12-page beginner-readiness
  chapter: scope preflight, HTTP orientation, browser observation, technology
  fingerprinting, bounded discovery, virtual hosts, public metadata, inputs and
  sessions, TLS and headers, findings, comprehensive reconnaissance, and review.
  The six existing labs keep their targets, flags, and behaviour; their
  `workbook:` paths now point at the new pages.
- Added **Educational material provenance** (`docs/EDUCATIONAL-PROVENANCE.md`)
  covering ownership, source-of-truth files, review status, framework references,
  synthetic content, AI assistance disclosure, licensing, and change control.
- Updated the README, Lite quickstart, platform overview, interface guide,
  exercise and RangeBox review, UI verification, privacy notice, and data
  deletion runbook for the combined workspace and the beginner track.
- Added desktop, light-theme, and mobile workspace screenshots to the docs.

### Licensing
- Added CyberChef attribution (Apache-2.0, external tool) to the third-party
  notices, About lab toolchains, and licence bundle.

## [2.5.5] - 2026-11-10

### Security
- Resolved the full open code-scanning set (595 alerts: 69 CodeQL, 526 Trivy).
- Fixed platform path handling in About, stress-test state, exercise testing,
  workbook chapters, and lab uploads; stack traces and daemon details are no
  longer returned to clients.
- Seed scripts now require their development passwords from the environment and
  never print or write them. Audit details redact password, secret, token, and
  key fields.
- Replaced the Admin VNC page's `innerHTML` interpolation with DOM/text nodes.
- Excluded intentionally vulnerable lab target applications from CodeQL; lab
  structure remains gated by `validate-lab.py` and `lab-release-proof.py`.
- Added path-scoped, documented Trivy suppressions for privileged lab images and
  the platform components that need root, privileged ports, or raw sockets.
- Removed `EXPOSE 22` and `RUN cd` from lab builds and replaced fake Stripe,
  Plaid, SendGrid, internal-API, and JWT values with explicit `FAKE_*` markers.

### Data integrity
- Added **Admin → System → Integrity** with a live ledger summary: entries,
  last write, unattributed writes in the last seven days, and covered tables.
- Added `scripts/db-integrity-check.sh` and `deploy/systemd/` units for daily
  quality, ledger, and checksum evidence and weekly signed manifests.
- Added an `occurred_at` index for the ledger status query.

### Upgrade
- Existing 2.5.4 databases upgrade in place. No destructive migration.
- No dependency or image pins changed in this release.

## [2.5.4] - 2026-11-10

### Lab metadata and curriculum
- Standardized all 149 lab manifests on the canonical `title`, `category`,
  `difficulty`, `estimated_time`, `prerequisites`, `learning_outcomes`,
  `mapped_skills`, `assessment_criteria`, and `mitre_attack` header.
- Replaced legacy `name`, `duration_minutes`, `objectives`, and
  `learning_objectives` keys with canonical keys while keeping legacy loading
  fallbacks for existing uploads and records.
- Generated `prerequisites` from the sequential unlock graph and added
  `mapped_skills` using the eight competency axes.
- Added a repeatable standardizer and static schema test for the full catalog.

### Learning outcomes
- Every lab now opens its outcomes with
  `# By completion students will be able to:` and lists 3-5 measurable
  outcomes.
- Rewrote vague openers such as `understand` and `learn` to observable actions;
  removed flag capture from learning outcomes and placed it under assessment.
- The learner exercise brief uses the same heading.

### MITRE ATT&CK
- Added at least one `tactic`, `technique`, `technique_name`, and `detection`
  mapping to every lab.
- Added an ATT&CK panel to the learner brief and exposed the mapping through
  the curriculum API.
- Added validation, a mapping service, and Alembic migration
  `0008_mitre_attack`.

### Instructor and student dashboards
- Added an instructor **Teaching focus** panel for learners one lab from a
  certificate, learners inactive 7+ days, and recent wins.
- Added a seven-day instructor learning snapshot: active students, labs
  completed, average score, and struggling students.
- Added per-course completion progress to student course cards and a workspace
  completion summary.
- Added a course readiness panel with a single next action for invite,
  exercises, assignments, or roster.
- Made student course cards real links with keyboard focus and accessible
  labels.

### Basic learning analytics
- Documented the five minimum metrics: lab started, lab completed, completion
  time, pass/fail, and retry count.
- Defined the instructor score as a transparent 0-100 participation score,
  adjusted for retries and hints.
- Reused existing session, completion, flag-attempt, and activity data rather
  than adding new learner tracking.

### Security and privacy
- Sanitized scenario markdown and validated external URLs to prevent stored
  XSS and unsafe link targets.
- Hardened report and certificate export privacy tests, CSV formula handling,
  and scoped instructor report exports.
- Closed leaked DB sessions, background tasks, and sockets during shutdown.
- Retried achievement writes after deadlocks and preserved the scheduler
  advisory lock without leaving an idle transaction.

### Reliability and performance
- Sized DB pools for worker count, added hot-path indexes, and dropped redundant
  primary-key indexes.
- Fixed the scheduler leader lock so background jobs do not run twice.
- Excluded runtime backend backups from deployment sync.
- Stripped byte-order marks from JSON and YAML release inputs.
- Added deployment performance guidance for the edge proxy.
- On the CTFd-hosted OCR stack at `.41`: increased the backend pool from 4+4 to
  6+6, tuned PostgreSQL planner settings, ran `VACUUM (ANALYZE)`, and reclaimed
  Docker build-cache and dangling-image space.

### Versions and migrations
- Platform, backend image, `/api/version`, and frontend package version:
  **2.5.4**.
- Alembic: `0007_lab_metadata`, `0008_mitre_attack`.
- Runtime pins remain Python 3.11, Node 22 build, PostgreSQL 15, Redis 7.2.

## [2.5.3] - 2026-11-08

### Competency radar
- Added a versioned eight-axis competency model and per-completion mapping
  snapshots.
- Added individual Baseline / Current / Target radar overlays and cohort
  median / interquartile / target overlays.
- Added per-axis evidence drill-down, separate self-confidence, provisional
  labels, mapping versions, and small-cohort suppression.
- Added the 50% assessment / 25% independent / 15% retained / 10% instructor
  scoring model with explicit weight coverage.

### Analytics privacy
- Added `analytics_min_cohort_size` and explicit available, suppressed, and
  no-evidence states to course and exercise analytics.
- Suppressed small cohorts in course feedback summaries and survey responses
  without exposing learner identities.

### Labs
- Recorded difficulty evidence for all 149 labs using platform analytics when
  `n>=5` and a labelled provisional static review otherwise.
- Added workbook and hint exemptions for instructor-led assessments.
- Added ADR 0005 accepting the lab bridge egress risk for 2.5.3.

### Accessibility
- Added PDF title, author, subject, keyword, and language metadata.
- Added the `session_accommodation_percent` timed-exercise accommodation.
- Fixed contrast defects in the skill matrix and analytics RAG badges and made
  activity and analytics table regions keyboard-focusable.
- Verified the competency radar with axe WCAG 2.2 AA at desktop and 320px.

### Supply chain
- Added OCI image version and revision labels.
- Refreshed and signed the supply-chain lock and signed the release tag.

### Privacy
- Added a public PIPEDA-aligned privacy notice at `/privacy`, linked from the
  footer and registration form. The notice uses `privacy@swocts.com` as the
  privacy contact and supplements the SWOCTS Privacy Policy.
- Added `docs/PRIVACY-NOTICE.md` and linked it from the privacy, erasure, and
  backup documentation and README.

### Reviews
- Added the v2.5.3 maintenance plan with the production analytics
  reconciliation, findings register, and release-health targets.
- Added `platform/backend/app/scripts/validate_analytics.py` for repeatable
  dashboard-to-source reconciliation.

## [2.5.2] - 2026-11-08

### Privacy settings
- Added a `privacy_default_on` platform setting under **Admin > Settings >
  Security**. Administrators can now set whether new admin browsers start with
  privacy mode enabled instead of relying on the hard-coded default.
- Added the current-browser privacy toggle to the same settings screen. The
  sidebar toggle remains available.
- Explicit per-browser choices still win. Legacy auto-written `"on"` values are
  treated as unset so a changed platform default reaches browsers that never
  made a choice.
- Documented the new location in the build notice, admin manual, release notes,
  and architecture settings table.

### Fixes
- Updated the analytics report test to expect the current six Skill DNA
  dimensions (the `leader` branch was added in 2.5.0).

## [2.5.1] - 2026-11-08

### Licence compliance
- Pinned Redis to `7.2-alpine` (BSD-3-Clause). Redis 7.4+ is RSALv2/SSPLv1 and
  is not a drop-in replacement without a licence review.
- Replaced `mysqlclient` (GPL-2.0) with MIT-licensed PyMySQL in the two web
  labs, and added SPDX GPL-2.0 headers to the Scapy-based PCAP generators with a
  documented mixed-licence exception.
- Removed the vendored Microsoft symbol table; the memory lab now generates it
  at image-build time from Microsoft's public symbol server.
- Pinned the third-party INetSim image to a reviewed digest and removed the
  breach-derived RockYou download from RangeBox.
- Rebuilt `THIRD_PARTY_NOTICES.md` and `THIRD_PARTY_LICENSES/`, corrected the
  psycopg and fpdf2 entries, and added the missing container, toolchain,
  vendored-binary, icon, and skill notices.
- Added `scripts/check-licences.py` and wired it into the quality workflow.

### About and build information
- Added an authenticated `/about` page with release, platform, branding,
  component, licence, and SBOM inventory.
- Added the generated `app/data/about` inventory, CycloneDX SBOMs, and
  `scripts/generate-about.py`.
- Documented the SWOCTS mark ownership and Avery Chaykoski design credit in
  `BRANDING.md`, the licence notices, and the About page.

### Privacy controls
- Admin accounts now default to privacy mode on when no explicit preference is
  stored.
- Usernames, emails, display names, and student IDs are masked consistently in
  admin tables, pending approvals, sessions, VPN peers, the user-details and
  edit-account dialogs, instructor tables, and activity actor names.
- Hovering or focusing a masked value reveals it. Administrators manage the
  current-browser toggle and the default for new admin browsers under
  **Admin > Settings > Security**.

### Course workspace cleanup
- Removed the Content, Achievements, and hidden Assignments panes from the
  course workspace. Overview, Feedback, and the instructor Analytics tab remain.
- Course links from an exercise now return to the course Overview.

## [2.5.0] - 2026-11-08

### Organizational course health
- Redesigned Academy → Courses around organizational course health: student
  satisfaction, instructor engagement, response rate, knowledge-check
  participation, and a prioritized action list.
- Added a private two-way feedback loop: students use the existing survey engine
  for a course check-in, instructors add coaching notes, and the summary
  aggregates check-ins, exercise pulse surveys, reactions, and coaching.
- Removed the public scoreboard from the course workspace. Detailed metrics
  remain private and descriptive; no ranking is shown.
- Added minimum-sample and data-source labels so a small response set is not
  presented as a trend.

### Optional knowledge checks
- Added optional exercise benchmarks with 2–3 randomized questions per attempt,
  unlimited re-attempts, explanations, and primary references.
- Added 10 certification-aligned lab banks and 11 track fallback banks, covering
  every exercise without making the check a gate.
- Added four benchmark achievements: Quiz Ace, Quiz Explorer, Quiz Scholar, and
  Quiz Comeback.
- Added quiz evidence to Cyber DNA (Builder and Explorer) and a Knowledge checks
  card on the profile.
- Added post-quiz experience ratings for satisfaction, relevance, usefulness,
  and ease of use; these feed the course health report.
- Added a CI validator for question banks and a documented expansion format.

### Certificates
- Added a server-rendered certificate PDF, copy-verification-link and LinkedIn
  share actions, a share panel, and Open Graph/Twitter metadata.
- Added a warning when a certificate still uses the login handle, with a link to
  set the printed name.
- Preserved earned certificates when bonus labs are added by excluding
  non-certificate labs from the level requirement.

### Labs and host validation
- Added the EXIF Metadata Investigation lab and beginner workbook.
- Certified Ubuntu 24.04 LTS for 2.4.1; 2.5.0 inherits the certified baseline.
- Fixed VPN forwarding by moving the VPN accepts into `DOCKER-USER`, added the
  missing Docker bridge UFW rule, and added the `ocr-network-tap` image.
- Raised the MS-SQL lab `max_connect_errors` threshold, corrected the remote
  credentials, and removed the trailing newline from the flag file.

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
  label now shows `Solid · Blue` instead of the old double-encoded middle dot, and dashes,
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
