# SWOCTS Cyber Range Release 3

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.

Status: **major feature release**. Release 3 adds Cyber DNA 2026.14, the Cyber GPS
active/fading signal, the RangeBox workspace refinements, a community events
calendar under Events, and production hardening. No database schema change is
required beyond the existing `0014_performance_indexes` head.

## Release 3 highlights

- **Cyber DNA 2026.14.** Scores are capped at 99, each branch decays from its
  own last practice date, the profile reports a 40-hour continuing-education
  target and a 30-day trend, and spider-chart points grow with evidence
  strength.
- **Cyber GPS signal.** The GPS shows an active or fading practice signal and
  names quiet domains as fading interest signals.
- **RangeBox workspace.** Stream-quality presets, Ctrl+Alt+Del, native
  fullscreen, flag capture, a text-only file guard, a pop-out window, and an
  independently scrolling workbook reader.
- **Community events.** The Events tab keeps platform events and adds an
  Around the area calendar for SWOCTS Hub and Cyber Hive YXU meetups.
- **Production hardening.** Valkey 9.1.3, the Docker socket proxy, backup
  volume ownership, the runtime integrity manifest, and the signed release key.

## Previous release: 2.7.0

## 2.7.0 highlights

- **Level quizzes.** Completed levels show a Quiz action only when an active
  quiz bank exists. The Beginner track ships with checks for all four stages.
- **VPN-only target guidance.** When a lab is launched without RangeBox, the
  panel now shows the computed target IP and the hosts-file mapping. RangeBox
  sessions keep addresses hidden unless `show_target_ips` is set.
- **Reliability.** WireGuard clients receive the `10.255.0.0/16` route on the
  VPN server, and lab creation no longer removes the network of a session that
  is still starting or running.

## Level quizzes

- The track API reports `has_quiz` per level. The frontend renders the Quiz
  button only for a completed level with an active bank, so an empty modal is
  no longer possible.
- Beginner banks: Stage 1 has 5 questions, Stage 2 has 5, Stage 3 has 4, and
  Stage 4 has 4. The passing score is 70.
- A submission returns the score, the correct count, per-question
  explanations, and the pass/fail result. Attempts are stored per learner.
- Seed or update the banks after deploying:

  ```bash
  docker exec -e PYTHONPATH=/app ocr-backend \
    python -m app.scripts.seed_level_quizzes
  ```

  The seed script is idempotent. It replaces the questions for each level and
  leaves existing attempts intact.

## VPN-only target guidance

- A VPN-only session exposes `hostname`, the computed `ip`, and the
  hosts-file mapping in the exercise panel.
- A RangeBox session keeps the same fields hidden unless the lab sets
  `show_target_ips`, because the desktop already provides in-browser access.
- The reveal is computed from the session's lab network; it does not expose
  other learners or the host management network.

## Reliability

- `scripts/setup-range-server.sh` installs `10.255.0.0/16 dev wg0` in
  `PostUp`/`PostDown`. Existing hosts can run
  `sudo bash scripts/fix-wireguard-client-route.sh`.
- Lab cleanup checks for a newer `starting`/`running` session for the same user
  and lab before removing a network, so a stop/relaunch no longer turns the new
  lab into a VPN-only session by accident.

## Release artefact

- `v2.7.0` is an annotated Git tag. It is **not GPG-signed** in this workspace.
- The supply-chain lock is signed by the SWOCTS Cyber Range release key.
- Sign the tag on the release workstation if a signed tag is required.

## Upgrade

1. Pull `v2.7.0` or the current `main`.
2. Back up the database and the erasure ledger.
3. Rebuild the backend and frontend:

   ```bash
   cd ~/opencyberrange/platform
   docker compose -f docker-compose.prod.yml up -d --build backend frontend
   ```

4. Confirm `/health` and `/api/version` report `2.7.0`.
5. Seed the level quiz banks with the command above.
6. Open a completed level and confirm the Quiz button appears; complete a
   fresh account's level and confirm it does not appear before completion.
7. Launch one VPN-only lab and confirm the target IP and hosts mapping render.

Existing 2.6.0 databases upgrade in place. The quiz tables already exist in the
2.6.0 schema, so this release adds data, not migrations. If you re-seed a bank,
avoid reordering its options after learners have attempted it, because stored
answers reference option indices.

See `CHANGELOG.md` for the itemised list.

# SWOCTS Cyber Range 2.6.0

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.

Status: **feature release**. 2.6.0 adds Grade 10-12 Digital Frontier labs, event
certificates, the WireGuard route correction, and the Cyber DNA `2026.13`
event-participation correction. APIs and existing certificate formats remain
compatible; existing VPN configs must be re-downloaded.

## Highlights

- **Grade 10-12 labs.** Lost-phone MFA recovery, media provenance, and a crypto
  rug-pull investigation join the K-12 pathway, with workbooks, quizzes, badges,
  titles, certification/learning pathways, and NICE mappings.
- **Event certificates.** Participation, placement, and trophy-challenge
  certificates carry the event logo and sponsor marks, work as JSON or PDF, and
  verify publicly with an `OCR-EVT-` ID. Existing credential privacy settings
  apply.
- **VPN route correction.** Clients use a `/32` address in `10.255.x.y` and
  route only their own lab `/24`, removing overlap with common home networks.
- **Cyber DNA 2026.13.** Raw event joins no longer add Leader; event lab
  completions and success badges still count.

## Event certificates

- Awards: participation, 1st/2nd/3rd place, First Blood, Clean Sweep, and Perfect
  Event.
- Certificates use deterministic
  `OCR-EVT-<competition>-<user>-<award>-<digest>` IDs and include the event logo
  and up to six sponsor marks in the PDF.
- Participation is available to every approved, opted-in participant after the
  event ends. Placement and trophy awards require the matching event achievement.
- Public verification returns event and award metadata only, never scores or
  account details. The certificate opt-out disables public verification and
  hides the QR code.
- The competition page lists earned certificates, and the certificate and
  verification pages handle event IDs alongside track certificates. The public
  form validates track and event ID formats before submission.
- See `docs/EVENT-CERTIFICATES.md` and `docs/SKILL-DNA.md`.

## New labs

- Grade 10: recover an account after a lost phone and a stale MFA method.
- Grade 11: verify the provenance and edit history of a media file.
- Grade 12: investigate a crypto token rug-pull using on-chain and community
  evidence.

Sensitive sextortion and legal content remains instructor-led and is not
self-paced.

## VPN configuration update

VPN clients now use a `/32` address in the `10.255.x.y` range and route only
the learner's own lab `/24`. This removes the old overlap with common home
networks caused by a `/16` client address and a `10.100.0.0/10`-sized route.

**Existing VPN configs must be re-downloaded.** If your tunnel stopped working,
open **Dashboard → VPN Configuration**, download a fresh config, remove the old
tunnel, and import the new one. The server-side peer is re-registered by the
migration; the old address is retired.

## Cyber DNA 2026.13

- Removed raw event participation from Leader.
- Event lab completions continue to count as normal lab work.
- Placement and trophy achievements still contribute through the achievement
  signal.
- Participation certificates are credentials, not Cyber DNA evidence.

## Release artefact

- `v2.6.0` is an annotated Git tag. It is **not GPG-signed** in this workspace.
- The supply-chain lock is signed by the SWOCTS Cyber Range release key.
- Sign the tag on the release workstation if a signed tag is required. The lock
  signature remains valid independently.

## Upgrade

1. Pull `v2.6.0` or the current `main`.
2. Back up the database and the erasure ledger.
3. Rebuild the backend and frontend:

   ```bash
   cd ~/opencyberrange/platform
   docker compose -f docker-compose.prod.yml up -d --build backend frontend
   ```

4. Confirm `/health` and `/api/version` report `2.6.0`.
5. Re-download VPN configs from **Dashboard → VPN Configuration** and verify the
   tunnel opens a lab.
6. After an event ends, open the event page and verify the certificate JSON, PDF,
   and public verification link with a test participant.

Existing 2.5.x databases upgrade in place. The VPN migration reallocates existing
peers; event certificates reuse the existing competition and achievement tables,
so no destructive schema change ships with this release.

See `CHANGELOG.md` for the itemised list.

# SWOCTS Cyber Range 2.5.5

SWOCTS Cyber Range is powered by OpenCyberRange.

Status: **patch release**. 2.5.5 closes the open code-scanning set and adds a
live database-integrity status to the admin portal, with a scheduled host check
for quality, ledger, and signed checksum evidence.

## Highlights

- **Security remediation.** The full open code-scanning set was reviewed:
  595 alerts (69 CodeQL, 526 Trivy). Platform path handling, stack-trace
  responses, seed-password handling, audit redaction, and the Admin VNC page are
  fixed. Intentionally vulnerable lab targets are excluded from CodeQL, and
  Trivy suppressions are path-scoped and documented in `.trivyignore.yaml`.
- **Data integrity status.** **Admin → System → Integrity** shows ledger
  entries, the last recorded write, unattributed writes in the last seven days,
  and the 16 covered critical tables. The existing System health grid also shows
  a **Data integrity** item.
- **Scheduled verification.** `scripts/db-integrity-check.sh` and
  `deploy/systemd/` run daily quality, ledger, and checksum checks and write a
  weekly signed manifest outside the database.

## Security

- About licence/SBOM downloads, stress-test state, exercise-test state, and
  workbook chapter deletion select existing paths from directory listings.
- Lab uploads rebuild the extraction target and ZIP entries from single path
  components and verify containment with `os.path.commonpath`.
- Stack traces and daemon details are no longer returned from RangeBox status,
  Docker disk usage, image cleanup, lab discovery, workbook upload/build, or
  walkthrough processing.
- Development seeds require `DEMO_FEATURE_PASSWORD`,
  `DEMO_ANALYTICS_PASSWORD`, `CAREER_DEMO_PASSWORD`,
  `DEMO_INSTRUCTOR_PASSWORD`, and `DEMO_STUDENT_PASSWORD`; they never print or
  write those values.
- Audit details redact password, secret, token, and key fields before logging.
- Lab and template target applications are excluded from CodeQL because their
  command injection, SQL injection, path traversal, and reflected XSS are the
  exercise content.
- Two CodeQL false positives were dismissed with recorded reasons: the
  requirements-specifier regex and the audit action/boolean flags.

## Data integrity

- The admin status is read-only and does not run the full chain or quality audit
  inside a web request. Full verification runs from the host schedule.
- `scripts/db-integrity-check.sh` uses `flock`, writes JSON evidence under
  `/var/lib/ocr-integrity` by default, and prunes after 90 days.
- `deploy/systemd/ocr-db-integrity.timer` runs daily at 02:30 UTC with a
  randomized delay. `ocr-db-integrity-alert@.service` records failures.
- Signed manifests require `DB_INTEGRITY_KEY` in
  `/etc/opencyberrange/integrity.env` (root-only). Keep the key and evidence
  off the database host for tamper evidence.

## Upgrade

1. Pull `v2.5.5` or the current `main`.
2. Back up the database and the erasure ledger.
3. Rebuild the backend and frontend:

   ```bash
   cd ~/opencyberrange/platform
   docker compose -f docker-compose.prod.yml up -d --build backend frontend
   ```

4. Confirm `/health` and `/api/version` report `2.5.5`.
5. Open **Admin → System → Integrity** and confirm the ledger is active.
6. Install the daily timer from `deploy/systemd/` if it is not already present.

Existing 2.5.4 databases upgrade in place. No destructive migration and no
dependency or image-pin changes ship in this release.

# SWOCTS Cyber Range 2.5.4

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.
Status: **patch release**. 2.5.4 makes lab metadata machine-readable, makes
learning outcomes measurable, adds MITRE ATT&CK alignment, and gives instructors
a seven-day learning snapshot. It also includes the security, reliability, and
database-pool fixes shipped after 2.5.3.

## Highlights

- All **149 labs** use the canonical metadata header: title, category,
  difficulty, estimated time, prerequisites, learning outcomes, mapped skills,
  assessment criteria, and MITRE ATT&CK.
- Every lab lists **3-5 measurable outcomes** under the heading
  **“By completion students will be able to:”**.
- Every lab declares a **MITRE ATT&CK tactic, technique, and detection
  opportunity**, shown in the learner brief.
- Instructor dashboard now shows **Students Active**, **Labs Completed**,
  **Average Score**, and **Struggling Students** for the last seven days.
- Student course cards show the learner’s own completion progress.
- Instructor **Teaching focus** surfaces near-certificate learners, inactive
  learners, and recent wins.

## Labs and metadata

- Added `title`, `estimated_time`, `learning_outcomes`, `prerequisites`,
  `mapped_skills`, `assessment_criteria`, and `mitre_attack` to every lab.
- Prerequisites mirror the sequential unlock graph, including previous-level
  labs and the previous lab in the same level.
- Competency mapping now uses authored `mapped_skills`; the old
  track/category heuristic remains as a fallback.
- Added a repeatable standardizer and a static catalog schema test.

## Analytics

- Documented the five minimum metrics: lab started, lab completed, completion
  time, pass/fail, and retry count.
- Added the seven-day instructor learning snapshot and struggling-student
  signal.
- Reused existing session, completion, flag-attempt, and activity data.

## Security and reliability

- Sanitized scenario markdown and validated external URLs.
- Hardened report and certificate privacy tests and CSV formula handling.
- Closed leaked DB sessions, background tasks, and sockets.
- Fixed scheduler leader locking and achievement-write deadlock retries.
- Sized DB pools for worker count, added hot-path indexes, and dropped redundant
  primary-key indexes.
- Tuned the CTFd-hosted OCR stack at `.41` with a 6+6 pool, PostgreSQL planner
  settings, vacuum/analyze, and Docker space cleanup.

## Version and migration notes

- Platform version: **2.5.4**
- Alembic migrations: **`0007_lab_metadata`**, **`0008_mitre_attack`**
- Runtime pins: Python 3.11, Node 22 build, PostgreSQL 15, Redis 7.2
- Existing 2.5.3 databases upgrade in place; no destructive data migration.

## Verification

- Backend suite: **176 passed** (non-DB), plus DB-backed metadata, dashboard,
  competency, analytics, and authorization tests.
- Lab metadata schema: **149/149 valid**.
- Frontend ESLint and production build: passed.
- Dev and production OCR stacks: healthy, API and exercise routes return 200.

---

# SWOCTS Cyber Range 2.5.3

SWOCTS Cyber Range is powered by OpenCyberRange.

Edition: **Professional** — Community / Academic plus analytics, reporting,
cohort analysis, competency evidence, accreditation support, and research
exports.
Status: **maintenance release**. 2.5.3 closes the analytics small-group
suppression finding, adds the versioned eight-axis competency radar, records
lab difficulty evidence for all 149 labs, and closes the accessibility and
supply-chain evidence gaps recorded against 2.5.2.

## Competency radar

- Eight stable competency axes: Network & Systems, Web & API, Identity &
  Access, Incident & Forensics, OSINT, Malware Analysis, OT/ICS, and AI
  Security.
- Individual view shows Baseline, Current, and Target overlays.
- Cohort view shows median, interquartile band, and target, and suppresses
  cohorts below the configured minimum size.
- Every axis opens a drill-down with contributing labs, assessments, recency,
  evidence count, model/mapping version, and observed / self-reported /
  instructor source counts.
- Scoring uses 50% assessment, 25% independent completion, 15% retained, and
  10% instructor evidence. Missing components stay visible as provisional with
  weight coverage rather than being silently redistributed.
- Self-confidence is displayed separately and is not part of the competency
  score.
- Per-completion mapping snapshots are stored so historical reports keep the
  mapping that was current when the completion happened.

## Analytics privacy

- Added `analytics_min_cohort_size` (default 5) and explicit **available**,
  **suppressed**, and **no_evidence** states to course and exercise analytics.
- Course feedback summaries and survey responses suppress small cohorts and do
  not expose learner usernames or emails in suppressed payloads.
- Reports and exports exclude suppressed cohorts from aggregate totals.

## Labs and evidence

- `validate-lab.py --all`: **149 labs, 0 errors, 0 warnings**.
- `lab-release-proof.py`: **149 pass, 0 review, 0 fail**.
- Difficulty evidence is observed platform analytics when `n>=5`; otherwise it
  is a labelled provisional student-tester review. The source, sample size,
  quality, and review date are recorded in each `lab.yaml`.
- Instructor-led assessments carry explicit workbook and hint exemptions.
- Added ADR 0005: the lab bridge egress risk is explicitly accepted for 2.5.3,
  with per-lab allowlisting deferred to the next release.

## Accessibility

- Added `/lang`, title, author, subject, and keyword metadata to report and
  certificate PDFs. Full PDF/UA tagging remains open.
- Added the `session_accommodation_percent` setting (100–300%) for timed
  exercises. It scales both the initial session length and extensions.
- Fixed WCAG AA contrast defects in the skill matrix and analytics RAG badges.
- Made activity and analytics table regions keyboard-focusable.
- Competency radar routes pass axe WCAG 2.2 AA at 1280×900 and 320×800 with no
  page-level overflow at 200% text. Report data tables scroll horizontally at
  200% text, which WCAG 1.4.10 permits for two-dimensional data.

## Supply chain and release engineering

- Added OCI image labels for title, description, version, revision, source, and
  licence.
- Refreshed and signed `supply-chain.lock.json`; the release tag is signed with
  the same release key.
- Development and production run the same commit and report `2.5.3`.
- Demo feature-test data remains development-only and is absent from
  production.

## Upgrade notes

1. Take a database snapshot before upgrading.
2. Pull the current `main` commit or the `v2.5.3` tag.
3. Rebuild the backend and frontend images.
4. Restart the backend once so the competency snapshot columns, mapping
   backfill, and new platform settings are applied. The migration is
   idempotent and additive.
5. Confirm `/health` and `/api/version` report `2.5.3`.
6. Open **Admin > Settings > Labs** and review **Timed Exercise
   Accommodation**; leave it at `100%` unless a learner has an approved plan.
7. Open **Admin > Settings > Security** and confirm **Analytics Minimum
   Cohort** is `5` or the value required by local policy.
8. If the host uses the prebuild workflow, run `scripts/prebuild-labs.sh` to
   refresh stable `ocr-lab/*:latest` images.
9. Rebuild the workbook wiki and user manual after pulling the documentation.

## Previous releases

2.5.2 added the administrator privacy default and corrected the analytics
report test for the six-dimension Skill DNA model. 2.5.1 added the
licence-compliance, About/build-info, privacy-control, and course-workspace
cleanup changes. 2.5.0 added organizational course health, two-way feedback,
optional knowledge checks, certificates, the Cyber DNA tester trait, the
celebration wall, database integrity, and deleted-user resilience. See
`CHANGELOG.md` for the complete history.
