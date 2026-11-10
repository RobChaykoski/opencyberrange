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
